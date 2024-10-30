create table audit
(
    tg_id int,
    fio TEXT,
    action TEXT,
    date TEXT
);

create table code
(
    tg_id int,
    code int
);

create unique index code_tg_id_uindex
	on code (tg_id);

create table privilege
(
    tg_id int not null,
    supervisor int default 0 not null
);

create table spammers
(
    tg_id int
);

create unique index spammers_tg_id_uindex
	on spammers (tg_id);

create table stats
(
    date TEXT,
    action TEXT
);

create table users
(
    tg_id INTEGER not null,
    fio TEXT,
    email TEXT,
    approved integer,
    login TEXT
);

create unique index users_tg_id_IDX
	on users (tg_id);

