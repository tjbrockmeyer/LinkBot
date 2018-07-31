
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
    remindee_id             bigint,
    remind_at               timestamp,
    reason                  text
);

CREATE TABLE quotes (
    server_id               bigint references servers(server_id),
    id                      integer primary key,
    author                  text,
    quote                   text
);

CREATE TABLE suggestions (
    id                      serial primary key,
    suggestion              text unique
);
