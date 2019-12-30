from neo4jdb import Session


async def delete_reminders_for_user(session: Session, u_id):
    """ Deletes all reminders that are associated with the given user. """

    await session.run(
        "MATCH (:User {id: {u_id}})<-[:REMINDING]-(r:Reminder)\n"
        "DETACH DELETE r", u_id=u_id)


async def create_reminder(session: Session, u_id, remind_at, reason):
    """ Create a reminder that is set to remind the given user at the given time for the given reason. """

    await session.run(
        "MATCH (u:User {id: {u_id}})\n"
        "CREATE (u)<-[:REMINDING]-(:Reminder {at: {at}, reason: {reason}})",
        u_id=u_id, at=remind_at, reason=reason)


async def get_reminders_before(session: Session, dtime):
    """ Return a tuple (ID, u_id, at, reason) for each reminder that will occur before the given datetime. """

    results = await session.run(
        "MATCH (r:Reminder)-[:REMINDING]->(u:User)\n"
        "WHERE r.at < {dt}\n"
        "RETURN ID(r), u.id, r.at, r.reason", dt=dtime)
    return results.values()


async def delete_reminders_with_ids(session: Session, obj_ids):
    """ Delete all reminders that have object ids present in the given list. """

    await session.run(
        "MATCH (r:Reminder)-[:REMINDING]->(:User)\n"
        "WHERE ID(r) in {ids}\n"
        "DETACH DELETE r", ids=obj_ids)
