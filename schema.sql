-- drop table if exists entries;
-- create table entries (
--   id integer primary key autoincrement,
--   title text not null,
--   text text not null
-- );

drop table if exists transistors;
CREATE TABLE transistors (
        id INTEGER primary key autoincrement,
        name VARCHAR NOT NULL,
        markname VARCHAR,
        type_ INTEGER,
        korpus INTEGER,
        descr VARCHAR,
        amount INTEGER,
        path_file VARCHAR,
        userid INTEGER,
        FOREIGN KEY(type_) REFERENCES type_ (id),
        FOREIGN KEY(korpus) REFERENCES korpus (id),
        FOREIGN KEY(userid) REFERENCES users (id)
);


drop table if exists type_;
CREATE TABLE type_ (
        id INTEGER primary key autoincrement,
        type_name VARCHAR
);


drop table if exists korpus;
CREATE TABLE korpus (
        id INTEGER primary key autoincrement,
        korpus_name VARCHAR
);


drop table if exists users;
CREATE TABLE users (
        id INTEGER primary key autoincrement,
        username VARCHAR NOT NULL,
        password VARCHAR NOT NULL,
        status INTEGER,
        UNIQUE (username)
);

