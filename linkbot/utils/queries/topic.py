from neo4jdb import Session


async def get_guild_topics(session: Session, g_id):
    """ Return the names of all created topics for the given guild. """

    results = await session.run(
        "MATCH (g:Guild {id: {g_id}})-[:HAS_TOPIC]->(t:Topic)\n"
        "OPTIONAL MATCH (t)<-[r:SUBSCRIBED_TO]-(:Member)\n"
        "RETURN t.name, count(r) as subCount", g_id=g_id)
    return results.values()


async def create_topic(session: Session, g_id, name):
    """ Create a topic for the given guild with the given name if it does not already exist. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "MERGE (g)-[:HAS_TOPIC]->(:Topic {name: {name}})", g_id=g_id, name=name)


async def get_topic(session: Session, g_id, name):
    """ Get the ID() for the topic of the given guild that has the given name. """

    result = await session.run(
        "MATCH (g:Guild {id: {g_id}})-[:HAS_TOPIC]->(t:Topic {name: {name}})\n"
        "RETURN ID(t) as id", g_id=g_id, name=name)
    return result.single()


async def create_sub_to_topic(session: Session, g_id, m_id, name):
    """ Create a subscription relationship between the given member and the given topic of the given guild. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})-[:HAS_TOPIC]->(t:Topic {name: {name}})\n"
        "MATCH (g)<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User {id: {m_id}})\n"
        "MERGE (t)<-[:SUBSCRIBED_TO]-(m)", g_id=g_id, m_id=m_id, name=name)


async def delete_sub_to_topic(session: Session, g_id, m_id, name):
    """ Delete the relationship between the given member and the given topic of the given guild. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User {id: {m_id}})\n"
        "MATCH (m)-[r:SUBSCRIBED_TO]->(t:Topic {name: {name}})\n"
        "DELETE r", g_id=g_id, m_id=m_id, name=name)


async def get_member_subscriptions(session: Session, g_id, m_id):
    """ Return a list of the names of all topics of the given guild that the member is subscribed to. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User {id: {m_id}})\n"
        "MATCH (m)-[:SUBSCRIBED_TO]->(t:Topic)\n"
        "RETURN collect(t.name)", g_id=g_id, m_id=m_id)
    return results.values()[0][0]


async def get_topic_subs(session: Session, g_id, name):
    """ Return a list of all members of the given guild that are subscribed to the named topic. """

    results = await session.run(
        "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
        "MATCH (m)-[:SUBSCRIBED_TO]->(t:Topic {name: {name}})\n"
        "RETURN collect(u.id)", g_id=g_id, name=name)
    return results.values()[0][0]
