from datetime import date

from neo4jdb import Session


async def get_guild_birthdays(session: Session, g_id):
    """ Return the user ids and birthdays of members in the given guild that have registered birthdays. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
        "WHERE exists(m.birthday)\n"
        "RETURN u.id, m.birthday", g_id=g_id)
    return [(x[0], x[1].to_native()) for x in results.records()]


async def set_birthday(session: Session, g_id, m_id, bday):
    """ Set the birthday property for the given member of the given guild. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "SET m.birthday = {bday}", g_id=g_id, m_id=m_id, bday=bday)


async def remove_birthday(session: Session, g_id, m_id):
    """ Remove the birthday property for the given member of the given guild. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "REMOVE m.birthday", g_id=g_id, m_id=m_id)


async def get_unrecognized_birthdays(session: Session, g_id):
    """ Return a list of user ids for members of the given server that have a birthday today
        and it has not yet been recognized. """

    today = date.today()
    today_y1 = date(1, today.month, today.day)
    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member {birthday: {today_y1}})-[:USER]->(u:User)\n"
        "WHERE not exists(m.lastCongrats) OR m.lastCongrats <> {today}\n"
        "RETURN collect(u.id)", g_id=g_id, today=today, today_y1=today_y1)
    return results.values()[0][0]


async def set_birthday_recognition(session: Session, g_id, m_ids):
    """ Set the birthday congradulation date to today for the given members of the given server. """

    today = date.today()
    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
        "WHERE u.id in {m_ids}\n"
        "SET m.lastCongrats = {today}", g_id=g_id, m_ids=m_ids, today=today)
