
CREATE TABLE servers (
    server_id               bigint primary key,
    entry_role              bigint
);

CREATE TABLE users (
    member_id               bigint primary key,
    is_admin                boolean,
    birthday                date
);

CREATE TABLE reminders (
    remindee                bigint references users(member_id),
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
