drop table if exists Books;
drop table if exists Authors;
drop table if exists Writes;
drop table if exists Customers;
drop table if exists Rate_book;
drop table if exists Rate_opinion;
drop table if exists Order_book;

create table Books (isbn char(14) primary key,
                    title varchar(128) not null,
                    authors varchar(256),
                    publisher varchar(64),
                    year_of_publication integer,
                    quantity_left integer,
                    price real,
                    format char(9) check (format = 'hardcover' or format = 'paperback') ,
                    keywords varchar(32),
                    subject varchar(32));

create table Authors (author_id integer primary key,
                      name varchar(128));

create table Customers (login_name varchar(32) primary key,
                        full_name varchar(128) not null,
                        password varchar(16) not null,
                        credit_card_no varchar(16),
                        address varchar(256),
                        phone_no char(8));

create table Writes (author_id integer,
                    isbn char(14),
                    primary key (author_id, isbn),
                    foreign key (author_id) references Authors,
                    foreign key (isbn) references Books);

create table Order_book (order_id integer primary key autoincrement,
                         login_name varchar(32),
                         isbn char(14),
                         order_date date not null,
                         status varchar(16) check (status = 'completed' or status = 'processing' or status = 'in delivery'),
                         quantity integer,
                         unique (login_name, isbn),
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

Insert into Books values ('978-1449389673', 'Photoshop Elements 9: The Missing Manual','Barbara Brundage', 'Pogue Press',1992,5,20,'hardcover','keywords none', 'Computer');
