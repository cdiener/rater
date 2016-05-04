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
app.config.from_object("config")

class LoginForm(Form):
    token = PasswordField('Enter your Token:', [validators.Required(),
    validators.AnyOf(app.config['USERS'].keys(), message="Invalid token!")])

class PersonForm(Form):
    pos = SelectField('What do you think is the position of the applicant?',
    [validators.Required()], choices=[('0', 'Undergrad'),
    ('1', 'M.Sc., Ph.D. student or health professional'),
    ('2', 'Postdoc, Associate Prof. or M.D.'), ('3', 'Principal Investigator')])
    inst = SelectField('How do you rate the institution?', [validators.Required()],
    choices=[('0', 'dubious'), ('1', 'average'), ('2', 'national leader'),
    ('3', 'international leader')])
    dist = SelectField('How do you rate the travel distance?', [validators.Required()],
    choices=[('0', 'local'), ('1', 'national'), ('2', 'international'),
    ('3', 'international leader')])

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
            return redirect(url_for('login', next=request.url))
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
    return render_template('login.html', form=form)

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
        cur = g.db.execute(abstract_count)
        nabstot = cur.fetchone()[0]
    return render_template('index.html', nrev=nrev, ntot=ntot, nabsrev=nabsrev,
        nabstot=nabstot, user=session['user'], role=session['role'])

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
    print(p)
    form = PersonForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute(insert_person_rating, (p[0], session['user'], form.pos.data,
        form.inst.data, form.dist.data))
        g.db.commit()
        session['rated'] += 1
        return redirect(url_for('added'))
    return render_template('applicants.html', p=p, rated=rated, form=form,
        user=session['user'], role=session['role'])

@app.route('/added')
def added():
    return render_template('added.html', rated=session['rated'],
        user=session['user'], role=session['role'])

if __name__ == '__main__':
    app.run()
