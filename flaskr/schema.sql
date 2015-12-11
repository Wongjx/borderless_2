drop table if exists Order_book;
drop table if exists Rate_opinion;
drop table if exists Rate_book;
drop table if exists Authors_write;
drop table if exists Books;
drop table if exists Customers;

create table Books (isbn char(14) primary key,
                    title varchar(128) not null,
                    publisher varchar(64),
                    year_of_publication integer,
                    quantity_left integer,
                    price real,
                    format char(9) check (format = 'hardcover' or format = 'paperback') ,
                    subject varchar(32));

create table Authors_write (aw_id integer primary key autoincrement,
                            name varchar(128),
                            isbn char(14),
                            unique (name, isbn),
                            foreign key (isbn) references Books);

create table Customers (login_name varchar(32) primary key,
                        full_name varchar(128) not null,
                        password varchar(16) not null,
                        credit_card_no varchar(16),
                        address varchar(256),
                        phone_no char(8));

create table Order_book (order_id integer primary key autoincrement,
                         login_name varchar(32),
                         isbn char(14),
                         order_date date not null,
                         quantity integer,
                         foreign key (login_name) references Customers,
                         foreign key (isbn) references Books);

create table Rate_book (rb_id integer primary key autoincrement,
                        isbn char(14),
                        login_name varchar(32),
                        score integer check (score <= 10 and score >= 0),
                        comment varchar(2048),
                        date date,
                        unique (isbn, login_name),
                        foreign key (isbn) references Books,
                        foreign key (login_name) references Customers);

create table Rate_opinion (ro_id integer primary key autoincrement,
                           rater_id varchar(32),
                           rated_id varchar(32),
                           isbn char(14),
                           rating integer check (rating >= 0 and rating <= 2),
                           unique (rater_id, rated_id, isbn),
                           foreign key (rater_id) references Customers(login_name),
                           foreign key (rated_id) references Rate_book(login_name),
                           foreign key (isbn) references Rate_book,
                           check (rated_id <> rater_id));
