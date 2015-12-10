#all the imports

import sqlite3
from contextlib import closing
from flask import Flask,request,session,g,redirect,url_for, abort, render_template,flash,make_response
import datetime, time
import re

#configuration

# DATABASE = 'C://Users//.nagareboshi.ritsuke//PycharmProjects//borderless_2//flaskr//tmp//flaskr.db'
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

def search_query_wrapper(query,parameter):
    return "{0} and {1} like ?".format(query, parameter)

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
        return e

def find_authors(isbn):
    author_list=db_query('select name from Authors_write where isbn==?',[isbn])
    authors=""
    for author in author_list:
        authors+=author['name']+","
    return authors[:-1]

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


## ROUTES
@app.route('/main', methods=['GET'])
def main():
    login_name = session['user']['login_name']
    if request.method == 'GET':
        # login_name=request.args['login_name']
        print login_name
        if not session['logged_in']:
            return redirect(url_for('login'))
        else:
            error = None
            book_list = db_query('select * from Books where quantity_left>0')
            for book in book_list:
                book['authors']=find_authors(book['isbn'])
            return render_template('main.html',book_list=book_list)

@app.route('/order', methods=['POST'])
def order():
    login_name = session['user']['login_name']
    request_path = request.headers['Referer']
    if request.method == 'POST':
        order_date=datetime.datetime.now()
        order_date=order_date.strftime("%Y-%m-%d|%H:%M:%S")
        status="processing"
        error=None

        count=0
        for k in request.form:
            if 'isbn' in k:
                isbn=k[5:-3]
                quantity=int(request.form[k]) # string will not be passed, input type='integer'
                if quantity<1:
                    continue
                else:
                    # decrement if quantity ordered > quantity left
                    count+=quantity
                    g.db.execute('update Books set quantity_left = quantity_left - 1 where isbn=? and quantity_left>?',[isbn,quantity]) #decrement number of book available
                    g.db.execute('insert into Order_book (login_name,isbn,order_date,status,quantity) VALUES (?,?,?,?,?)',[login_name,isbn,order_date,status,quantity]) #insert order
                    g.db.commit()
        if count <1: #Nothing ordered
            error="Invalid quantity. Please order more than 1 book."
            return redirect(request_path)
        return redirect(url_for('order_complete',date=order_date,login_name=login_name,error=error)) # redirect to order_complete with date and username


@app.route('/order_complete/<date>/<login_name>', methods=['GET','POST'])
def order_complete(date,login_name):
    # retreive orders from date and login_name
    orders = db_query('Select * from Order_book, Books where login_name = ? and order_date=? and Order_book.isbn==Books.isbn', [login_name,date])
    total_price=0
    total_quantity=0
    for order in orders:
        total_price+=order["price"] # calculate total price
        total_quantity+=order["quantity"]
    query="""
            select OB2.isbn, B.title ,sum(OB1.quantity) as sales_count, B.subject
            from Order_book OB1, Order_book OB2, Books B
            where OB1.login_name = OB2.login_name
            and OB2.isbn = B.isbn
            and OB1.isbn = ? /*insert isbn*/
            and OB1.isbn <> OB2.isbn
            group by OB2.isbn
            order by  sales_count desc
            limit 4
        """
    for order in orders:
        recommendations=db_query(query,[order['isbn']])
        order['recommendations']=recommendations
    return render_template('order_complete.html',orders=orders,date=date,total_price=total_price,total_quantity=total_quantity)

@app.route('/book/<isbn>', methods=['GET','POST'])
def book(isbn):
    login_name=session['user']['login_name']
    error=None
    if not login_name:
        redirect(url_for('login'))
    else:
        book = db_query('Select * from Books where isbn = ?', [isbn], one=True)
        if book is None:
            error = 'Invalid ISBN'
            return redirect(url_for('main'))
        else:
            query="""
                select RB.rb_id, RB.isbn, RB.login_name, RB.score, RB.comment, RB.date, A.usefulness_score
                from Rate_book RB, (select isbn, rated_id , avg(rating) as usefulness_score 
                from (select RO.isbn, RO.rated_id, RO.rating
                    from Rate_opinion RO
                    where exists 
                        (select *
                        from Rate_book
                        where isbn = ?
                        and isbn = RO.isbn
                        )
                    )
                group by rated_id
                ) A
                where RB.isbn = A.isbn
                and RB.login_name = A.rated_id
            """
            avg_score=None
            if request.method=='POST':
                action=request.form['action']
                if action=='find_reviews':
                    opinion_query="""
                    select RB.rb_id, RB.isbn, RB.login_name, RB.score, RB.comment, RB.date, A.usefulness_score
                    from Rate_book RB, (select isbn, rated_id , avg(rating) as usefulness_score 
                        from (select RO.isbn, RO.rated_id, RO.rating
                            from Rate_opinion RO
                            where exists 
                                (select *
                                from Rate_book
                                where isbn = ?
                                and isbn = RO.isbn
                                )
                            )
                        group by rated_id
                        ) A
                    where RB.isbn = A.isbn
                    and RB.login_name = A.rated_id
                    order by A.usefulness_score desc
                    limit ?"""
                    n=request.form['n']
                    opinions=db_query(opinion_query,[isbn,n])
                elif action=='rate_review':
                    rating=request.form['rating']
                    rated_id=request.form['opinion_id']  
                    if rated_id!=session.user.login_name:
                        try:                  
                            g.db.execute('insert into Rate_opinion values (?,?,?,?,?)',[None,login_name,rated_id,isbn,rating])
                            g.db.commit()
                        except:
                            error="You have rated this review!"
                    else:
                        error="You cannot rate your own review!"
                    opinions=db_query(query, [isbn])
                    #sql to rate opinion
                elif action=='rate_book':
                    score=request.form['score']
                    comment=request.form['comment']
                    date=datetime.datetime.now()
                    date=date.strftime("%Y-%m-%d|%H:%M:%S")
                    g.db.execute('insert into Rate_book values (?,?,?,?,?,?)',[None,isbn,login_name,score,comment,date])
                    g.db.commit()
                    opinions=db_query(query, [isbn])
            book['authors']=find_authors(book['isbn'])
            exist_comment=db_query('Select * from Rate_book where isbn = ? and login_name = ?', [isbn,login_name], one=True)
            # find if comment made by this user exist, dont allow him to comment
            if request.method=="GET":
                opinions=db_query(query, [isbn])               
        
        return render_template('individual_book.html',book=book,opinions=opinions,exist_comment=exist_comment,avg_score=avg_score,error=error)

@app.route('/search', methods=['GET','POST'])
def search():
    error = None
    if request.method == 'POST':        
        # Check if advanced search
        if request.form.has_key("advance_search"):
            query="""
            select B2.isbn, B2.title, B2.year_of_publication, B2.publisher, B2.subject, B2.quantity_left,C.avg_score
            from Books B2, 
                (select RB.isbn, avg(RB.score) as avg_score
                from Rate_book RB
                where RB.isbn in
                    (select B.isbn
                    from Books B
                    where exists
                        (select * 
                        from Authors_write A
                        where A.isbn = B.isbn
                        and A.name like ?
                        ) /*insert author name*/
                    and B.title like ? /*insert title*/
                    and B.subject like ? /*insert subject*/
                    and B.publisher like ? /*insert publisher*/
                    %s /*insert year*/
                    ) 
                group by RB.isbn
                ) C
            where C.isbn = B2.isbn
            and C.avg_score>=?
            order by C.avg_score desc
            
            """
            book_rating = request.form['book_rating']
            author='%'+'%' 
            publisher = '%'+'%'
            subject='%'+'%' 
            book_name='%'+'%'
            #Check author     
            if request.form['author'] !="":
                author = '%'+ request.form['author'] +'%' 
                                
            #Check publisher
            if request.form['publisher'] != "":
                publisher = '%'+ request.form['publisher']+'%'
                
            #Check Genre
            if request.form['subject'] != "None":
                subject = '%'+request.form['subject']+'%'

            #Check title
            if request.form['book_name'] !="":
                book_name = '%'+request.form['book_name']+'%'

            if request.form['year_of_publication'] !="":
                year_of_publication = "and B.year_of_publication="+request.form['year_of_publication']
                query=query%year_of_publication
            else:
                query=query%''
                
            params=[author,book_name,subject,publisher,int(book_rating)]
            # params=['%%','%%','%%','%'+request.form['book_name']+'%',5]  
        else:
            query = "select * from Books where title like ?"
            book_name = request.form['book_name']
            params=['%'+book_name+'%']

# 
        books = db_query( query, params)
        params={}
        params['author']=author.strip("%")
        params['publisher']=publisher.strip("%")
        params['subject']=subject.strip("%")
        params['book_name']=book_name.strip("%")
        params['avg_score']=book_rating
        if len(books)<1:
            error = 'We are sorry! Unable to find what you are looking for!'
            return render_template('search_result.html',error=error)
        else:
            for book in books:
                book['authors']=find_authors(book['isbn'])
        return render_template('search_result.html',books=books,params=params)



@app.route('/profile/<login_name>', methods=['GET'])
def profile(login_name):
    # retreive orders from date and login_name
    user = db_query('Select * from Customers where login_name = ? ', [login_name], one=True)
    orders = db_query('Select * from Order_book where login_name = ?', [login_name])
    opinions = db_query('select B.title,  B.isbn, RB.score, RB.comment from Books B, Rate_book RB where RB.isbn = B.isbn and RB.login_name = ?',[login_name])
    ratings = db_query('select C.full_name, C.login_name, B.title, B.isbn, RO.rating,RB.comment from Books B, Rate_opinion RO,Rate_book RB, Customers C where RO.isbn = B.isbn and RO.rated_id = C.login_name and RO.rated_id= RB.login_name and RO.rater_id = ? order by C.login_name',[login_name])
    return render_template('user_profile.html',user=user, orders = orders,opinions=opinions,ratings=ratings)
# =======
    # orders = db_query('Select * from Order_book where login_name = ? order by order_id', [login_name])
    # book_ratings = db_query('Select * from Rate_book where login_name = ? order by score', [login_name])
    # comment_ratings = db_query('Select * from Rate_opinion where rater_id = ? order by rating', [login_name])
    # return render_template('user_profile.html',user=user, orders = orders, book_ratings = [book_ratings,len(book_ratings)], comment_ratings = [comment_ratings,len(comment_ratings)])
# >>>>>>> 2f9b98161190375a9a2c0fc9a4dbcae2114cc9bc


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        ccn = request.form['ccn']
        user = db_query('select * from Customers where login_name = ?', [username], one=True)
        if user is None:
            ## New user sign up
            # g.db.execute('insert into Customers (login_name,full_name,password,credit_card_no,address,phone_no) VALUES (?,?,?,?,?,?)',[username,name,password,ccn,address,phone])
            # g.db.commit()
            if name == "":
                error="Please enter a valid name."
                return render_template('signup.html', error=error)
            elif password == "":
                error="Please enter a valid password."
                return render_template('signup.html', error=error)
            e = db_insert('insert into Customers (login_name,full_name,password,credit_card_no,address,phone_no) VALUES (?,?,?,?,?,?)',[username,name,password,ccn,address,phone])
            if e!=True:
                return render_template('signup.html',error=str(e))
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
        if the_username == USERNAME:
            if password == PASSWORD:
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
    if request.method == 'POST':
        return render_template('admin.html')
    else:
        return render_template('admin.html')

@app.route('/admin/newbook', methods=['GET','POST'])
def admin_newbook():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        authors = request.form['authors']
        authors.replace(" ","")
        authorlist = re.split(';',authors)
        subject = request.form['subject']
        publisher = request.form['publisher']
        price = request.form['price']
        year_published = request.form['year_published']
        format = request.form['format']
        quantity = request.form['quantity']
        e = db_insert('insert into Books (isbn,title,publisher,year_of_publication,quantity_left,price,format,subject) VALUES (?,?,?,?,?,?,?,?)',[isbn,title,publisher,year_published,quantity,price,format,subject])
        if e!= True:
            return render_template('admin_newbook.html', error = str(e))
        # for author in authorlist:
        #     db_insert()
        flash('Book successfully added')
        return render_template('admin.html')

    elif request.method == 'GET':
        return render_template('admin_newbook.html')

@app.route('/admin/inventory', methods=['GET','POST'])
def admin_invent():
    return render_template('admin inventory.html')#, error = 'Admin Inventory: Work in progress')

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
    with closing(connect_db()) as db:
        with app.open_resource('populate_tables.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
