#all the imports

import sqlite3
from contextlib import closing
from flask import Flask,request,session,g,redirect,url_for, abort, render_template,flash

#configuration
# DATABASE = 'C://Users//.nagareboshi.ritsuke//PycharmProjects//borderless//flaskr//tmp//flaskr.db'
# DATABASE = '/home/jx/borderless/flaskr/tmp/flaskr.db'
DATABASE = 'D:/Year 3 term 6/Database/Borderless/flaskr/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little appllcaition ;)
app = Flask(__name__)
app.config.from_object(__name__)

#Load app configuration from file
# app.config.from_envvar('FLASK_SETTINGS',silent = True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g.db = connect_db()
    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db (query, args=()):
    try:
        cur = get_db().execute(query, args)
        return True
    except Exception, e:
        print e
        return False

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


## ROUTES
@app.route('/main/<login_name>', methods=['GET','POST'])
def main(login_name):

    if request.method == 'POST':
        print request.form
        orders=[] # PT - list of isbn of book cutomers want to order
        for k in request.form:
            if 'isbn' in k:
                isbn=request.form[k]

        return redirect(url_for('order_complete/%s/%s' % date,username ))
    elif request.method == 'GET':
        # login_name=request.args['login_name']
        print login_name
        if not login_name:
            return redirect(url_for('login'))
        else:
            error = None
            book_list = query_db('select * from Books')
            print book_list
            return render_template('main.html',book_list=book_list, login_name=login_name)

@app.route('/order', methods=['GET','POST'])
def order():
    if request.method == 'POST':
        g.db.execute('insert into entries (title, text) values (?, ?)',
                     [request.form['title'], request.form['text']])
        g.db.commit()
        flash('Order was successfully posted')
        return redirect(url_for('order'))
    elif request.method == 'GET':
        return render_template('order_complete.html')

@app.route('/order_complete/<date>/<username>', methods=['GET','POST'])
def order_complete():
    return render_template('order_complete.html')

@app.route('/book/<login_name>/<isbn>', methods=['GET'])
def book(login_name,isbn):
    book = query_db('Select * from Books where isbn = ?', [isbn], one=True)
    rate=query_db('Select * from Rate_book where isbn = ? and login_name = ?', [isbn,login_name], one=True)
    if book is None:
        error = 'Invalid ISBN'
        return redirect(url_for('main'))
    return render_template('individual_book.html',book=book)

@app.route('/search', methods=['GET','POST'])
def search():
    error = None
    if request.method == 'POST':
        book_name = request.form['book_name']
        book = query_db('Select * from Books where title like ?', ['%'+book_name+'%'], one=True)
        if book is None:
            error = 'Invalid ISBN'
            return render_template('search_result.html',error=error)
    return render_template('search_result.html',search=book)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        #Username not correct
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        ccn = request.form['ccn']
        user = query_db('select * from Customers where login_name = ?', [username], one=True)
        print user
        if user is None:
            ## New user sign up
            g.db.execute('insert into Customers (login_name,full_name,password,credit_card_no,address,phone_no) VALUES (?,?,?,?,?,?)',[username,name,password,ccn,address,phone])
            g.db.commit()
            flash('Sign up successful')
            return redirect(url_for('login'))
        else:
            ## Existing account with same login name
            error = 'Username already in use'
    ## 'GET' route
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Username not correct
        the_username = request.form['username']
        password = request.form['password']
        user = query_db('select * from Customers where login_name = ?', [the_username], one=True)
        if user is None:
            error = 'Invalid Username'
        else:
            if password == user['password']:
                session['logged_in'] = True
                session ['user'] = user
                flash('You were logged in')
                return redirect(url_for('main', login_name=the_username))
            else:
                error = 'Invalid password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()

## RUN WITH PYTHON SHELL TO INIT DB
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
