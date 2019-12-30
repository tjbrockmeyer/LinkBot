from neo4jdb import Session


async def get_member_is_admin(session: Session, g_id, m_id):
    """ Return true if the user has an admin relationship to the server, false otherwise. """

    result = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:ADMIN_OF]-(:Member)-[:USER]->(u:User {id: {m_id}})\n"
        "RETURN count(u) > 0 as c", g_id=g_id, m_id=m_id)
    return result.single()[0]


async def get_guild_admins(session: Session, g_id):
    """ Return a list of user ids for all admins in the given guild. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:ADMIN_OF]-(:Member)-[:USER]->(u:User)\n"
        "RETURN collect(u.id)", g_id=g_id)
    return results.values()[0][0]


async def create_admins(session: Session, g_id, m_ids):
    """ Create the admin relationship for members of a given server. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
        "WHERE u.id in {m_ids}\n"
        "MERGE (g)<-[:ADMIN_OF]-(m)", g_id=g_id, m_ids=m_ids)


async def delete_admins(session: Session, g_id, m_ids):
    """ Delete the admin relationship for admins of a given server. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[r:ADMIN_OF]-(:Member)-[:USER]->(u:User)\n"
        "WHERE u.id in {m_ids}\n"
        "DELETE r", g_id=g_id, m_ids=m_ids)
