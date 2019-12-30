from neo4jdb import Session


async def get_quote_with_ref(session: Session, g_id, ref):
    """ Return the quote tuple (u.id, q.text, q.ref) from the given guild that is
        registered with the given reference. """

    result = await session.run(
        "MATCH (q:Quote {ref: {ref}})<-[:SAID]-(m:Member)-[:MEMBER_OF]->(:Guild {id: {g_id}})\n"
        "MATCH (m)-[:USER]->(u:User)\n"
        "RETURN u.id, q.text, ID(q) as id", g_id=g_id, ref=ref)
    return result.single()


async def get_quotes_from_member(session: Session, g_id, m_id):
    """ Return all quote tuples (q.text, q.ref) that have been said by the given member of the given guild. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "MATCH (m)-[:SAID]->(q:Quote)\n"
        "RETURN q.text, q.ref", g_id=g_id, m_id=m_id)
    return results.values()


async def get_quote_starts_with(session: Session, g_id, m_id, starts_with):
    """ Return a quote tuple of (q.text, q.ref) from the given member of the given guild
        that starts with the given text. """

    result = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "MATCH (m)-[:SAID]->(q:Quote)\n"
        "WHERE q.text STARTS WITH {starts_with}\n"
        "RETURN q.text, q.ref, ID(q) as id", g_id=g_id, m_id=m_id, starts_with=starts_with)
    return result.single()


async def get_guild_quotes(session: Session, g_id):
    """ Return all quotes for the given guild. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:SAID]->(q:Quote)\n"
        "MATCH (m)-[:USER]->(u:User)\n"
        "RETURN u.id, q.text, q.ref", g_id=g_id)
    return results.values()


async def create_quote(session: Session, g_id, m_id, text):
    """ Create a quote object and connect it to the given member of the given guild. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "MERGE (m)-[:SAID]->(:Quote {text: {text}})", g_id=g_id, m_id=m_id, text=text)


async def set_quote_reference(session: Session, g_id, m_id, starts_with, ref):
    """ Set the reference text for the quote by the given member of the given guild that
        starts with the given text to the given reference. """

    await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
        "MATCH (m)-[:SAID]->(q:Quote)\n"
        "WHERE q.text STARTS WITH {starts_with}\n"
        "SET q.ref = {ref}", g_id=g_id, m_id=m_id, starts_with=starts_with, ref=ref)


async def remove_quote_reference(session: Session, g_id, ref):
    """ Remove the reference for the quote with the given reference from the given guild. """

    await session.run(
        "MATCH (q:Quote {ref: {ref}})<-[:SAID]-(:Member)-[:MEMBER_OF]->(:Guild {id: {g_id}})\n"
        "REMOVE q.ref", g_id=g_id, ref=ref)
