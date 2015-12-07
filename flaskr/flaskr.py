#all the imports

import sqlite3
from contextlib import closing
from flask import Flask,request,session,g,redirect,url_for, abort, render_template,flash
import datetime, time

#configuration
DATABASE = 'C://Users//.nagareboshi.ritsuke//PycharmProjects//borderless_2//flaskr//tmp//flaskr.db'
# DATABASE = '/home/jx/borderless/flaskr/tmp/flaskr.db'
# DATABASE = 'D:/Year 3 term 6/Database/Borderless/flaskr/tmp/flaskr.db'
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

def db_query(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def db_insert (query, args=()):
    try:
        db=get_db()
        cur = db.execute(query, args)
        db.commit()
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
@app.route('/main', methods=['GET','POST'])
def main():
    login_name = session['user']['login_name']
    # if request.method == 'POST':
    #     order_date=datetime.datetime.now()
    #     order_date=order_date.strftime("%Y-%m-%d|%H:%M:%S")
    #     status="processing"
    #     quantity=1
    #     for k in request.form:
    #         if 'isbn' in k:
    #             isbn=request.form[k]
    #             g.db.execute('update Books set quantity_left = quantity_left - 1 where isbn=?',[isbn]) #decrement number of book available
    #             g.db.execute('insert into Order_book (login_name,isbn,order_date,status,quantity) VALUES (?,?,?,?,?)',[login_name,isbn,order_date,status,quantity]) #insert order
    #             g.db.commit()
    #             # time.sleep(1)
    #     return redirect(url_for('order_complete',date=order_date,login_name=login_name)) # redirect to order_complete with date and username
    if request.method == 'GET':
        # login_name=request.args['login_name']
        print login_name
        if not session['logged_in']:
            return redirect(url_for('login'))
        else:
            error = None
            book_list = db_query('select * from Books where quantity_left>0')
            print book_list
            return render_template('main.html',book_list=book_list)


### Hidden routes order, opinion and rate_opinion
@app.route('/order', methods=['GET','POST'])
def order():
    login_name = session['user']['login_name']
    if request.method == 'POST':
        order_date=datetime.datetime.now()
        order_date=order_date.strftime("%Y-%m-%d|%H:%M:%S")
        status="processing"
        quantity=1
        # print "/n"
        # print "Request.form ===== " +str(request.form)
        # print "/n"
        if len(request.form) <=1:
            return redirect
        for k in request.form:
            if 'isbn' in k:
                isbn=request.form[k]
                # g.db.execute('update Books set quantity_left = quantity_left - 1 where isbn=?',[isbn]) #decrement number of book available
                g.db.execute('insert into Order_book (login_name,isbn,order_date,status,quantity) VALUES (?,?,?,?,?)',[login_name,isbn,order_date,status,quantity]) #insert order
                g.db.commit()
                # time.sleep(1)
        return redirect(url_for('order_complete',date=order_date,login_name=login_name)) # redirect to order_complete with date and username

# PT
    # elif request.method == 'GET':
    #     # login_name=request.args['login_name']
    #     if session['user']:
    #         error = None
    #         book_list = query_db('select * from Books where quantity_left>0')
    #         for book in book_list:
    #             author_list=query_db('select name from Authors where author_id in (select author_id from Writes where isbn==?)',[book['isbn']])
    #             authors=""
    #             for author in author_list:
    #                 authors+=author['name']+","
    #             book['authors']=authors[:-1]
    #         return render_template('main.html',book_list=book_list, login_name=login_name)
    #     else:
    #         return redirect(url_for('login'))

    elif request.method == 'GET':
        return render_template('order_complete.html')

@app.route('/order_complete/<date>/<login_name>', methods=['GET','POST'])
def order_complete(date,login_name):
    # retreive orders from date and login_name
    orders = db_query('Select * from Order_book, Books where login_name = ? and order_date=? and Order_book.isbn==Books.isbn', [login_name,date])
    total_price=0
    for order in orders:
        total_price+=order["price"] # calculate total price
    return render_template('order_complete.html',orders=orders,date=date,total_price=total_price)
# PT
# @app.route('/book/<login_name>/<isbn>', methods=['GET','POST'])
# def book(login_name,isbn):
    
#     book = query_db('Select * from Books where isbn = ?', [isbn], one=True)
#     author_list=query_db('select name from Authors where author_id in (select author_id from Writes where isbn==?)',[book['isbn']])
#     authors=""
#     for author in author_list:
#         authors+=author['name']+","
#     book['authors']=authors[:-1]
#     exist_comment=query_db('Select * from Rate_book where isbn = ? and login_name = ?', [isbn,login_name], one=True)
#     opinions=query_db('Select * from Rate_book where isbn = ?', [isbn])
#     for opinion in opinions:
#         avg_rating=query_db('select avg(rating) from Rate_opinion where rated_id in (select  login_name from Rate_book where isbn==? and login_name==?)',[opinion['isbn'],opinion['login_name']])
#         avg_rating=avg_rating[0]['avg(rating)']
#         if avg_rating<2 and avg_rating>=1:
#             avg_rating="Useful"
#         elif avg_rating>=2:
#             avg_rating="Very Useful"
#         else:
#             avg_rating="Useless"
#         opinion['avg_rating']=avg_rating
#     if book is None:
#         error = 'Invalid ISBN'
#         return redirect(url_for('main'))
#     if request.method == 'POST':
#         isbn=request.form['isbn']
#         if isbn:
#             order_date=datetime.datetime.now()
#             order_date=order_date.strftime("%Y-%m-%d|%H:%M:%S")
#             quantity=1
#             status="processing"
#             g.db.execute('update Books set quantity_left = quantity_left - 1 where isbn=?',[isbn]) #decrement number of book available
#             g.db.execute('insert into Order_book (login_name,isbn,order_date,status,quantity) VALUES (?,?,?,?,?)',[login_name,isbn,order_date,status,quantity]) #insert order
#             g.db.commit()
#             redirect(url_for('order_complete',date=order_date,login_name=login_name))
#         else:
#             usefulness=request.form['rating']
@app.route('/opinion', methods=['GET','POST'])
def opinion():
    return None

@app.route('/rate_opinion', methods=['GET','POST'])
def rate_opinion():
    return None

@app.route('/book/<isbn>', methods=['GET','POST'])
def book(isbn):
    if request.method == 'GET':
        book = db_query('Select * from Books where isbn = ?', [isbn], one=True)
        rate=db_query('Select * from Rate_book where isbn = ? and login_name = ?', [isbn,session['user']['login_name']], one=True)
        if book is None:
            error = 'Invalid ISBN'
            return redirect(url_for('main'))
        return render_template('individual_book.html',book=book)

@app.route('/search', methods=['GET','POST'])
def search():
    error = None
    if request.method == 'POST':
        book_name = request.form['book_name']
        book = db_query('Select * from Books where title like ?', ['%'+book_name+'%'])
        if book is None:
            error = 'Invalid ISBN'
            return render_template('search_result.html',error=error)
    return render_template('search_result.html',search=[book])

@app.route('/profile/<login_name>', methods=['GET'])
def profile(login_name):
    # retreive orders from date and login_name
    user = db_query('Select * from Customers where login_name = ? ', [login_name], one=True)
    orders = db_query('Select * from Order_book where login_name = ?', [login_name])
    return render_template('user_profile.html',user=user, orders = orders)


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
        user = db_query('select * from Customers where login_name = ?', [username], one=True)
        print user
        if user is None:
            ## New user sign up
            # g.db.execute('insert into Customers (login_name,full_name,password,credit_card_no,address,phone_no) VALUES (?,?,?,?,?,?)',[username,name,password,ccn,address,phone])
            # g.db.commit()
            db_insert('insert into Customers (login_name,full_name,password,credit_card_no,address,phone_no) VALUES (?,?,?,?,?,?)',[username,name,password,ccn,address,phone])
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
        if the_username == "admin":
            if password == "password":
                return redirect(url_for('admin'))
                # return render_template('admin inventory.html')
            else:
                return render_template('login.html',error= 'Invalid password')
        # user = query_db('select * from Customers where login_name = ?', [the_username], one=True)
        user = db_query('select * from Customers where login_name = ?', [the_username], one=True)
        if user is None:
            error = 'Invalid Username'
        else:
            if password == user['password']:
                session['logged_in'] = True
                session['user'] = user
                flash('You were logged in')
                return redirect(url_for('main'))
            else:
                error = 'Invalid password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('login'))

#### Admin Routes/Pages
@app.route('/admin', methods=['GET','POST'])
def admin():
    # if request.method == 'GET':
    #
    # elif request.method == 'POST':
    return render_template('admin.html')

@app.route('/admin/newbook', methods=['GET','POST'])
def admin_newbook():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        subject = request.form['subject']
        publisher = request.form['publisher']
        price = request.form['price']
        year_published = request.form['year_published']
        format = request.form['format']
        quantity = request.form['quantity']
        try:
            db_insert('insert into Books (isbn,title,publisher,year_of_publication,quantity_left,price,format,subject) VALUES (?,?,?,?,?,?,?,?,?)',[isbn,title,publisher,year_published,quantity,price,format,subject])
            flash('Book successfully added')
        except Exception as e:
            render_template(admin_newbook, error = str(e))
    elif request.method == 'GET':
        return render_template('admin_newbook.html')
    return render_template('admin.html')

@app.route('/admin/inventory', methods=['GET','POST'])
def admin_invent():
    return render_template('admin.html', error = 'Admin Inventory: Work in progress')

@app.route('/admin/statistics', methods=['GET','POST'])
def admin_stats():
    return render_template('admin.html', error = 'Admin Statistics: Work in progress')


if __name__ == '__main__':
    app.run()

## RUN WITH PYTHON SHELL TO INIT DB
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
