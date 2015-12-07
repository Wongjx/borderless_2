/*3*/
/*Account info*/
select * from Customers
where login_name = "xiexin2011" ; /*insert login_name*/

/*Full history of orders*/
select B.title, B.isbn, OB.quantity, OB.order_date  
from Order_book OB, Books B
where OB.isbn = B.isbn
and OB.login_name = 'xiexin2011'; /*insert login_name*/

/*Full history of feedbacks*/
select B.title,  B.isbn, RB.score, RB.comment
from Books B, Rate_book RB
where RB.isbn = B.isbn
and RB.login_name = 'xiexin2011'; /*insert login_name*/

/*list of feedbacks ranked wrt usefulness*/
select C.full_name, C.login_name, B.title, B.isbn, RO.rating
from Books B, Rate_opinion RO, Customers C
where RO.isbn = B.isbn
and RO.rated_id = C.login_name
and RO.rater_id = 'xiexin2011'; /*insert login_name*/;

/*insert Rate_book values*/
insert into Rate_book values (NULL,'978-0136079675', 'fengmeng1990',8,NULL,'2001-05-02');

/*insert Rate_opinion values*/
insert into Rate_opinion values (NULL,'zhouhuichan1990', 'zhengzhemin1991','978-0470523988',2);
