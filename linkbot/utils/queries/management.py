from neo4jdb import Session


async def create_constraints(session: Session):
    await session.run("CREATE CONSTRAINT ON (u:User) ASSERT u.id IS UNIQUE")
    await session.run("CREATE CONSTRAINT ON (g:Guild) ASSERT g.id IS UNIQUE")


async def create_indexes(session: Session):
    await session.run("CREATE INDEX ON :User(birthday)")
    await session.run("CREATE INDEX ON :Reminder(at)")
    await session.run("CREATE INDEX ON :Quote(ref)")


async def delete_node_with_id(session: Session, node_id):
    """ Delete and detach a node using its ID(). """

    await session.run("MATCH (n) WHERE ID(n) = {id} DETACH DELETE n", id=node_id)


async def sync_members(session: Session, g_id, m_ids):
    """ Members in the list will be created and/or connected with the given guild, and
        members not in the list will be disconnected. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
        "WHERE not u.id in {m_ids}\n"
        "WITH g, m\n"
        "MATCH (g)-[r]-(m)\n"
        "DELETE r\n"
        "CREATE (m)-[:OLD_MEMBER_OF]->(g)", g_id=g_id, m_ids=m_ids)
    await create_members(session, g_id, m_ids)


async def create_guild(session: Session, g_id):
    """ Create a guild object with the given guild id if it does not already exist. """

    await session.run("MERGE (:Guild {id: {g_id}})", g_id=g_id)


async def delete_guild(session: Session, g_id):
    """ Delete a guild object with the given id. This will delete all connected information. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})--(n)\n"
        "DETACH DELETE g, n", g_id=g_id)


async def create_members(session: Session, g_id, m_ids):
    """ Create user and member objects from the given list of user ids with links to the given guild. """

    await session.run(
        "MATCH (u:User)<-[:USER]-(m:Member)-[r:OLD_MEMBER_OF]->(g:Guild {id: {g_id}})\n"
        "WHERE u.id in {m_ids}\n"
        "DELETE r\n"
        "CREATE (m)-[:MEMBER_OF]->(g)", g_id=g_id, m_ids=m_ids)
    await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "FOREACH (v in {m_ids} |\n"
        "  MERGE (u:User {id: v})\n"
        "  MERGE (u)<-[:USER]-(m:Member)-[:MEMBER_OF]->(g))", g_id=g_id, m_ids=m_ids)


async def delete_member(session: Session, g_id, m_id):
    """ Remove the member status relationship between the given member and the given guild. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})<-[r:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "DELETE r\n"
        "CREATE (m)-[:OLD_MEMBER_OF]->(g)", g_id=g_id, m_id=m_id)
