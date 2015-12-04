drop table if exists enteries;
drop table if exists Books;
drop table if exists Customers;
drop table if exists Rate_book;
drop table if exists Rate_opinion;
drop table if exists Order_book;

-- create table entries (
--   id integer primary key autoincrement,
--   title text not null,
--   text tetx not null
-- );

create table Books (isbn char(14) primary key,
                    title varchar(128) not null,
                    authors varchar(256),
                    publisher varchar(64),
                    year_of_publication integer,
                    quantity_left integer,
                    price real,
                    format char(9) check (format = 'hardcover' or format = 'softcover') ,
                    keywords varchar(32),
                    subject varchar(32));

create table Customers (login_name varchar(16) primary key,
                        full_name varchar(128) not null,
                        password varchar(16) not null,
                        credit_card_no varchar(16),
                        address varchar(256),
                        phone_no integer);

create table Rate_book (isbn char(14),
                        login_name varchar(16),
                        score integer check (score <= 10 and score >= 1),
                        comment varchar(2048),
                        date date,
                        primary key (isbn, login_name),
                        foreign key (isbn) references Books(isbn),
                        foreign key (login_name) references Customers(login_name));

create table Rate_opinion (rater_id varchar(16),
                           rated_id varchar(16),
                           isbn char(14),
                           rating integer check (rating >= 0 and rating <= 2),
                           primary key (rater_id, rated_id, isbn),
                           foreign key (rater_id) references Customers(login_name),
                           foreign key (rated_id) references Customers(login_name),
                           foreign key (isbn) references Books(isbn),
                           check (rated_id <> rater_id));

create table Order_book (order_id integer,
                         login_name varchar(16),
						             isbn char(14),
                         order_date date not null,
                         status varchar(16) check (status = 'completed' or status = 'processing' or status = 'in delivery'),
                         quantity integer,
                         primary key (order_id),
                         foreign key (login_name) references Customers(login_name),
                         foreign key (isbn) references Books(isbn));

Insert into Books values ('978-1449389673', 'Photoshop Elements 9: The Missing Manual','Barbara Brundage', 'Pogue Press',1992,5,20,'hardcover','keywords none', 'subject here');
