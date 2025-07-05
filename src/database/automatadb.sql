create database if not exists automatadb;
use automatadb;

create table fa_headers(
	id int primary key auto_increment,
    name varchar(255) unique not null,
    type varchar(10) not null,
    start_state_name varchar(255) not null, -- eg q0 or A
    description text
);

create table fa_states(
	id int primary key auto_increment,
    fa_id int not null,
    name varchar(255)  not null, -- A or q1 or Dead
	is_accepting boolean not null default false,
    unique(fa_id,name),
    foreign key (fa_id) references fa_headers(id)
);

create table fa_symbols(
	id int primary key auto_increment,
    fa_id int not null,
    symbol_char varChar(50) not null, -- symbols like 1, 0 ,a or ep for epsilon
    unique(fa_id,symbol_char)
);

create table fa_transitons(
	id int primary key auto_increment,
    fa_id int not null,
    from_state_name varchar(255) not null,
    symbol_char varchar(50) not null,
    to_state_name varchar(255) not null,
    unique (fa_id,from_state_name,symbol_char,to_state_name)
);