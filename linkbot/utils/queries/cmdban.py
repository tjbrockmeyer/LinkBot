from neo4jdb import Session


async def create_command_ban(session: Session, g_id, m_id, cmd_name):
    """ Ban the given member of the given guild from using the given command. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "MERGE (m)<-[:CMD_BAN {name: {cmd_name}}]-(g)", g_id=g_id, m_id=m_id, cmd_name=cmd_name)


async def delete_command_ban(session: Session, g_id, m_id, cmd_name):
    """ Ban the given member of the given guild from using the given command. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})-[r:CMD_BAN {name: {cmd_name}}]->(:Member)-[:USER]->(:User {id: {m_id}})\n"
        "DELETE r", g_id=g_id, m_id=m_id, cmd_name=cmd_name)


async def get_member_is_banned_from_command(session: Session, g_id, m_id, cmd_name):
    """ Ban the given member of the given guild from using the given command. """

    result = await session.run(
        "MATCH (:Guild {id: {g_id}})-[r:CMD_BAN {name: {cmd_name}}]->(:Member)-[:USER]->(:User {id: {m_id}})\n"
        "RETURN count(r) > 0 as c", g_id=g_id, m_id=m_id, cmd_name=cmd_name)
    return result.single()[0]
