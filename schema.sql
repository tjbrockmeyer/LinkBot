

-- SERVER TABLES --

CREATE TABLE servers (
    server_id               bigint      primary key,
    entry_role              bigint,
    info_channel            bigint
);

CREATE TABLE admins (
    server_id               bigint      references servers(server_id),
    user_id                 bigint      not null,
    primary key (server_id, user_id)
);

CREATE TABLE birthdays (
    server_id               bigint      not null references servers(server_id),
    person                  text        not null,
    birthday                date        not null,
    last_congrats           integer     not null default(0)
);

CREATE TABLE quotes (
    server_id               bigint      references servers(server_id),
    id                      integer     not null,
    author                  text        not null,
    quote                   text        not null,
    primary key (server_id, id)
);

-- INDEPENDENT TABLES --

CREATE TABLE reminders (
    remindee_id             bigint      not null,
    remind_at               timestamp   not null,
    reason                  text
);

CREATE TABLE suggestions (
    id                      serial      primary key,
    suggestion              text        not null
);
