# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from queries import *
from functools import wraps
from contextlib import closing
from wtforms import SelectField, PasswordField, validators
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from os import urandom, path
import uuid
import pandas as pd

PERSON_COLS = (14, 0, 1 ,4, 2, 3, 8, 5, 7, 6, 9, 10, 11)

app = Flask(__name__)

if path.exists("deploy_conf.py"):
    app.config.from_pyfile("deploy_conf.py")
    print("Using deploy configuration...")
else:
    app.config.from_pyfile("config.py")
    print("Using mock configuration...")

# The forms
###########
rating_validator = validators.AnyOf(['0', '1', '2', '3', '4'],
    message="You forgot to select an option")

class LoginForm(Form):
    token = PasswordField('Enter your Token:', [validators.Required(),
    validators.AnyOf(app.config['USERS'].keys(), message="Invalid token!")])

class PersonForm(Form):
    pos = SelectField('What do YOU think is the position of the applicant?',
    [rating_validator], choices=[('100', 'Pick one..'), ('0', 'Undergrad'),
    ('1', 'M.Sc./Ph.D. student or health pro.'),
    ('2', 'Postdoc, Associate Prof. or M.D.'), ('3', 'Principal Investigator')])
    inst = SelectField('How do you rate the institution?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'dubious'), ('1', 'average'),
    ('2', 'national leader'), ('3', 'international leader')])
    dist = SelectField('How do you rate the travel distance?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'local'), ('1', 'national'),
    ('2', 'international')])
    topic = SelectField('How do you rate the research topic?',
    [rating_validator], choices=[('100', 'Pick one..'), ('0', '0 - bad'),
    ('1', '1 - average'), ('2', '2 - amazing')])

class AbstractForm(Form):
    abstract = SelectField('How do you rate the abstract(s)?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', '0 - insufficient'), ('1', '1 - barely acceptable'),
    ('2', '2 - acceptable'), ('3', '3 - pretty good'), ('4', '4 - amazing')])
    english = SelectField('How do you rate the quality of English?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'insufficient'), ('1', 'acceptable'),
    ('2', 'fluent')])

class ImportForm(Form):
    persons = FileField('Choose an applicant file', [FileAllowed(['.csv'])])
    posters = FileField('Choose a poster abstracts file', [FileAllowed(['.csv'])])
    talks = FileField('Choose a talk abstracts file', [FileAllowed(['.csv'])])
###########

# Utility functions
###########
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def add_fakes(db, n, base_id=1):
    from faker import Faker
    fake = Faker()
    for i in range(n):
        vals = (str(base_id+i), fake.first_name(), fake.last_name(), fake.email(),
            'NA', fake.date(), fake.military_ship(), fake.company(), fake.state(),
            fake.country(), 'Ph.D.', fake.job(), fake.sentence(), fake.sentence(),
            fake.text(750), fake.name(), fake.company(), fake.sentence(),
            fake.text(450), fake.name(), fake.company())
        db.execute(insert_complete, vals)
    db.commit()

def init_db(n=0):
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
    if n > 0: add_fakes(db, n)

def make_token(n, word=None):
    if word:
        return uuid.uuid5(uuid.NAMESPACE_DNS, word + app.config['SECRET_KEY']).hex[0:n]
    return uuid.uuid4().hex[0:n]

def tokenize(users):
    return {make_token(16, u[0]): u for u in users}

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
#########3

# Routes
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        token = form.token.data
        session['user'] = app.config['USERS'][token][0]
        session['role'] = app.config['USERS'][token][1]
        session['rated'] = 0
        flash('Thank you. Logging in...')
        return redirect(url_for('show_entries'))
    return render_template('login.html', form=form, n_user=len(app.config['USERS']))

@app.route('/')
@login_required
def show_entries():
    data = {}
    cur = g.db.execute(review_count, (session['user'],))
    data['nrev'] = cur.fetchone()[0]
    cur = g.db.execute("select count(*) from ratings")
    data['ntotrev'] = cur.fetchone()[0]
    cur = g.db.execute("select count(*) from abstracts")
    data['nabstotrev'] = cur.fetchone()[0]
    cur = g.db.execute(person_count)
    data['ntot'] = cur.fetchone()[0]
    cur = g.db.execute(abstract_count)
    data['nabstot'] = cur.fetchone()[0]
    cur = g.db.execute(abstract_rev_count, (session['user'],))
    data['nabsrev'] = cur.fetchone()[0]
    return render_template('index.html',user=session['user'],
        role=session['role'], **data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    session.pop('rated', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/applicants', methods=['POST', 'GET'])
@login_required
def rate_person():
    cur = g.db.execute(next_person, (session['user'],))
    p = cur.fetchone()
    form = PersonForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute(insert_person_rating, (p[0], session['user'], form.pos.data,
            form.inst.data, form.dist.data, form.topic.data))
        g.db.commit()
        session['rated'] += 1
        return redirect(url_for('added', type='applicant'))
    return render_template('applicants.html', p=p, form=form,
        user=session['user'], role=session['role'])

@app.route('/abstracts', methods=['POST', 'GET'])
@login_required
def rate_abstract():
    if session['role'] != 'all':
        return render_template('message.html', type='error', title='Nope...',
            message='You are not allowed to review abstracts :(',
            user=session['user'], role=session['role'])
    cur = g.db.execute(next_abstract, (session['user'],))
    a = cur.fetchone()
    form = AbstractForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute(insert_abstract_rating, (a[0], session['user'],
            form.abstract.data, form.english.data))
        g.db.commit()
        session['rated'] += 1
        return redirect(url_for('added', type='abstract'))
    return render_template('abstracts.html', a=a, form=form,
        user=session['user'], role=session['role'])

@app.route('/added/<type>')
@login_required
def added(type):
    return render_template('added.html', rated=session['rated'],
        user=session['user'], role=session['role'], type=type)

@app.route('/results')
@login_required
def results():
    persons = pd.read_sql("select * from persons", g.db)
    ratings = pd.read_sql(average_ratings, g.db)
    abstracts = pd.read_sql(average_abstracts, g.db)
    persons = pd.merge(persons, ratings, on='pid', how='left')
    persons = pd.merge(persons, abstracts, on='pid', how='left', suffixes=('_applicant', '_abstract'))

    persons["total"] = persons[['p_position', 'p_institution', 'p_distance',
        'p_topic', 'p_abstract']].sum(axis=1).fillna(0)
    persons = persons.sort_values(by="total", ascending=False)
    persons.to_csv('static/res.csv', encoding='utf-8')
    table = zip(range(1,persons.shape[0]+1), persons['first'] + ' ' + persons['last'],
        persons['institution'], persons['country'],
        persons['nrev_applicant'].fillna(0).astype(int).astype(str) +
        ' + ' + persons['nrev_abstract'].fillna(0).astype(int).astype(str),
        persons['total'].round(2))
    return render_template('results.html', table=table, user=session['user'],
        role=session['role'])

@app.route('/import', methods=['POST', 'GET'])
@login_required
def file_import():
    if session['role'] != 'all':
        return render_template('message.html', type='error', title='Nope...',
            message='You are not allowed to import data :(',
            user=session['user'], role=session['role'])
    form = ImportForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            p = pd.read_csv(request.files['persons'], skipinitialspace=True).fillna("NA")
            a_posters = pd.read_csv(request.files['posters'])
            a_talks = pd.read_csv(request.files['talks'])
            if p.shape[1] != 15:
                raise ValueError("Wrong numbers of columns in applicant data!")
            elif a_posters.shape[1] != 7:
                raise ValueError("Wrong numbers of columns in poster data!")
            elif a_talks.shape[1] != 8:
                raise ValueError("Wrong numbers of columns in talk data!")
        except BaseException as e:
            msg = 'Could not parse the files. Please ensure that the uploaded \
            files are CSV files that can be read by pandas. Error: ' + str(e)
            return render_template('message.html', type='error', title='Parse error',
                message=msg, user=session['user'], role=session['role'])
        p.ix[:, 4] = p.ix[:, 4].str.strip().str.lower()
        p.ix[:, 14] = p.ix[:, 14].astype('str')
        cur = g.db.execute(person_count)
        n = cur.fetchone()[0]
        inserter = zip(*[p.ix[:,i] for i in PERSON_COLS])
        g.db.executemany(insert_person, inserter)
        g.db.commit()
        cur = g.db.execute(all_emails)
        emails = [e[0] for e in cur.fetchall()]
        a_posters['Email'] = a_posters['Email'].str.strip().str.lower()
        a_talks['Email'] = a_talks['Email'].str.strip().str.lower()
        a_posters['matched'] = a_posters['Email'].isin(emails)
        a_talks['matched'] = a_talks['Email'].isin(emails)

        # The weird order and columns is due to errors in the form
        # design which we can not alter anymore
        a = a_posters.loc[a_posters.matched]
        inserter = zip(a.ix[:,3], a.ix[:,4], a.ix[:,6], a.ix[:,5], a.ix[:,2])
        g.db.executemany(update_poster, inserter)
        a = a_talks.loc[a_talks.matched]
        inserter = zip(a.ix[:,3], a.ix[:,4], a.ix[:,5], a.ix[:,6], a.ix[:,2])
        g.db.executemany(update_talk, inserter)
        g.db.commit()
        cur = g.db.execute(person_count)
        persons_added = cur.fetchone()[0] - n
        emails_not_found = a_posters.loc[a_posters.matched == False]['Email'].append(
            a_talks.loc[a_talks.matched == False]['Email'])
        emails_not_found = emails_not_found.unique()
        msg = 'Added {} new applicants. Unmatched Emails ({}): {}'.format(
            persons_added, len(emails_not_found), ', '.join(emails_not_found))
        return render_template('message.html', type='good', title='Added new data',
            message=msg, user=session['user'], role=session['role'])
    return render_template('import.html', form=form, user=session['user'],
        role=session['role'])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
