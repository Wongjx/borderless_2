/*1 Registration*/
insert into Customers values ('qinyuwei2011','QIN YUWEI','70nljygtr(,%b9w!','5387149260','7 Parsons Walk, Bridgeyate, Bristol, South Gloucestershire BS30 5WA, UK','86312075')
/*(login_name, full_name, password, credit_card_no, address, phone_no)*/;


/*2 Ordering*/
insert into Order_book values (NULL,'ngqiyang1989','978-1607140573','2013-11-07','completed',4)
/*(order_id, login_name, isbn, order_date, status, quantity)*/;


/*3 User Record*/
/*Account info*/
select * from Customers
where login_name = "xiexin2011" /*insert login_name*/;

/*Full history of orders*/
select B.title, B.isbn, OB.quantity, OB.order_date  
from Order_book OB, Books B
where OB.isbn = B.isbn
and OB.login_name = 'xiexin2011' /*insert login_name*/;

/*Full history of feedbacks*/
select B.title,  B.isbn, RB.score, RB.comment
from Books B, Rate_book RB
where RB.isbn = B.isbn
and RB.login_name = 'xiexin2011' /*insert login_name*/;

/*list of feedbacks ranked wrt usefulness*/
select C.full_name, C.login_name, B.title, B.isbn, RO.rating
from Books B, Rate_opinion RO, Customers C
where RO.isbn = B.isbn
and RO.rated_id = C.login_name
and RO.rater_id = 'xiexin2011' /*insert login_name*/;

/*4 New Book*/
insert into Books values ('978-0321474049','The Digital Photography Book','Peachpit Press','2006',7,82.38,'paperback',NULL,'Computer science')
/*(isbn, title, publisher, year_of_publication, quantity_left, price, format, keywords, subject) */;
insert into Authors_write values (NULL,'Nyan-Ping Bi','978-0887276897')
/*(aw_id, name, isbn) */;


/*5 Arrival of more copies*/
update Books
set quantity_left = quantity_left + 1 /*insert integer*/
where isbn = '978-0321474049' /*insert isbn*/;


/*6 Feedback Recordings*/
insert into Rate_book values (NULL,'978-0136079675', 'fengmeng1990',8,NULL,'2001-05-02') 
/*(rb_id, isbn, login_name, score, comment, date)*/;


/*7 Usefulness ratings*/
insert into Rate_opinion values (NULL,'zhouhuichan1990', 'zhengzhemin1991','978-0470523988',2) 
/*(ro_id, rater_id, rated_id, isbn, rating) */;


/*8 Book Browsing*/

/*Find books that have X title by X author and X publisher and X subject ordered by year*/
select B.isbn, B.title, B.year_of_publication, B.publisher, B.subject
from Books B
where exists
	(select * 
	from Authors_write A
	where A.isbn = B.isbn
	and A.name like '%%') /*insert author name*/
and B.title like '%%' /*insert title*/
and B.subject like '%%' /*insert subject*/
and B.publisher like '%%' /*insert publisher*/
order by B.year_of_publication desc
;

/*Find books that have X title by X author and X publisher and X subject ordered by avg feedback score*/
select B2.isbn, B2.title, B2.year_of_publication, B2.publisher, B2.subject, C.avg_score
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
			and A.name like '%%'
			) /*insert author name*/
		and B.title like '%%' /*insert title*/
		and B.subject like '%%' /*insert subject*/
		and B.publisher like '%mcgraw%' /*insert publisher*/
		) 
	group by RB.isbn
	) C
where C.isbn = B2.isbn
order by C.avg_score desc
;


/*9 Useful Feedbacks*/
select RB.rb_id, RB.isbn, RB.login_name, RB.score, RB.comment, RB.date, A.usefulness_score
from Rate_book RB, (select isbn, rated_id , avg(rating) as usefulness_score 
	from (select RO.isbn, RO.rated_id, RO.rating
		from Rate_opinion RO
		where exists 
			(select *
			from Rate_book
			where isbn = "978-0684801520" /*insert isbn*/
			and isbn = RO.isbn
			)
		)
	group by rated_id
	) A
where RB.isbn = A.isbn
and RB.login_name = A.rated_id
order by A.usefulness_score desc
limit 4 /*insert n. Note: limit n only applies when n < count(*) */
;


/*10 Book Recommendation*/


/*11 Monthly Stats*/
/*List of m most popular books*/
select OB.isbn, B.title, sum(OB.quantity) as order_count
from Order_book OB, Books B
where OB.isbn = B.isbn
and order_date like '%2015-12%' /*insert '%yyyy-mm%'*/
group by OB.isbn
order by order_count desc
limit 10 /*insert m. Note: limit m only applies when m < count(*) */
;

/*List of m most popular authors*/
select name, count(name) as author_count
from Authors_write
where isbn in 
	(select isbn
	from Order_book
	where order_date like '%2015-12%' /*insert '%yyyy-mm%'*/
	)
group by name
order by author_count desc
limit 5 /*insert m. Note: limit m only applies when m < count(*) */
;

/*List of m most popular publishers*/
select B.publisher, count(B.publisher) as publisher_count 
from Books B, Order_book OB 
where B.isbn = OB.isbn
and OB.order_date like '%2015-12%' /*insert '%yyyy-mm%'*/
group by publisher
order by publisher_count desc
limit 5 /*insert m. Note: limit m only applies when m < count(*) */
;
