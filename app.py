# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from queries import *
from functools import wraps
from contextlib import closing
from wtforms import SelectField, PasswordField, validators
from flask_wtf import Form

app = Flask(__name__)
app.config.from_pyfile("config.py")

rating_validator = validators.AnyOf(['0', '1', '2', '3', '4'],
    message="You forgot to select an option")

class LoginForm(Form):
    token = PasswordField('Enter your Token:', [validators.Required(),
    validators.AnyOf(app.config['USERS'].keys(), message="Invalid token!")])

class PersonForm(Form):
    pos = SelectField('What do you think is the position of the applicant?',
    [rating_validator], choices=[('100', 'Pick one..'), ('0', 'Undergrad'),
    ('1', 'M.Sc./Ph.D. student or health pro.'),
    ('2', 'Postdoc, Associate Prof. or M.D.'), ('3', 'Principal Investigator')])
    inst = SelectField('How do you rate the institution?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'dubious'), ('1', 'average'),
    ('2', 'national leader'), ('3', 'international leader')])
    dist = SelectField('How do you rate the travel distance?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'local'), ('1', 'national'),
    ('2', 'international')])

class AbstractForm(Form):
    topic = SelectField('How do you rate the reserach topic?',
    [rating_validator], choices=[('100', 'Pick one..'), ('0', '0 - bad'),
    ('1', '1 - average'), ('2', '2 - amazing')])
    abstract = SelectField('How do you rate the abstract(s)?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', '0 - insufficient'), ('1', '1 - barely acceptable'),
    ('2', '2 - acceptable'), ('3', '3 - pretty good'), ('4', '4 - amazing')])
    english = SelectField('How do you rate quality of English?', [rating_validator],
    choices=[('100', 'Pick one..'), ('0', 'insufficient'), ('1', 'acceptable'),
    ('2', 'fluent')])

class TopicForm(Form):
    topic = SelectField('How do you rate the reserach topic?',
    [rating_validator], choices=[('100', 'Pick one..'), ('0', '0 - bad'),
    ('1', '1 - average'), ('2', '2 - amazing')])

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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
    cur = g.db.execute(review_count, (session['user'],))
    nrev = cur.fetchone()[0]
    cur = g.db.execute(person_count)
    ntot = cur.fetchone()[0]
    nabsrev = nabstot = 0
    if session['role'] == 'all':
        cur = g.db.execute(abstract_rev_count, (session['user'],))
        nabsrev = cur.fetchone()[0]
    return render_template('index.html', nrev=nrev, ntot=ntot, nabsrev=nabsrev,
        user=session['user'], role=session['role'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    session.pop('rated', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/applicants', methods=['POST', 'GET'])
@login_required
def rate_person(rated=0):
    cur = g.db.execute(next_person, (session['user'],))
    p = cur.fetchone()
    form = PersonForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute(insert_abstract_rating, (p[0], session['user'], form.pos.data,
            form.inst.data, form.dist.data))
        g.db.commit()
        session['rated'] += 1
        return redirect(url_for('added', type='applicant'))
    return render_template('applicants.html', p=p, rated=rated, form=form,
        user=session['user'], role=session['role'])

@app.route('/abstracts', methods=['POST', 'GET'])
@login_required
def rate_abstract(rated=0):
    cur = g.db.execute(next_abstract, (session['user'],))
    a = cur.fetchone()
    has_abstract = a is not None and (a[2] or a[3])
    if has_abstract: form = AbstractForm(request.form)
    else: form = TopicForm(request.form)
    if request.method == 'POST' and form.validate():
        if has_abstract:
            g.db.execute(insert_abstract_rating, (a[0], session['user'],
                form.topic.data, form.abstract.data, form.english.data))
        else: g.db.execute(insert_abstract_rating, (a[0], session['user'],
            form.topic.data, 0, 0))
        g.db.commit()
        session['rated'] += 1
        return redirect(url_for('added', type='abstract'))
    return render_template('abstracts.html', a=a, rated=rated, form=form,
        user=session['user'], role=session['role'])

@app.route('/added/<type>')
def added(type):
    return render_template('added.html', rated=session['rated'],
        user=session['user'], role=session['role'], type=type)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
