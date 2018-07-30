
CREATE TABLE servers (
    server_id               bigint primary key,
    entry_role              bigint
);

CREATE TABLE admins (
    server_id               bigint references servers(server_id),
    user_id                 bigint
);

CREATE TABLE birthdays (
    server_id               bigint references servers(server_id),
    person                  text,
    birthday                date,
    last_congrats           integer default(0)
);

CREATE TABLE reminders (
    id                      serial primary key,
    remindee                bigint,
    remind_at               timestamp,
    reason                  text
);

CREATE TABLE quotes (
    id                      integer primary key,
    author                  text,
    quotes                  text
);

CREATE TABLE suggestions (
    id                      serial primary key,
    suggestion              text
);
