from neo4jdb import Session


async def get_entry_role(session: Session, g_id):
    """ Return the role id for the assigned entry-role of the given server. Return None if it does not exist. """

    result = await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "WHERE exists(g.entryRole)\n"
        "RETURN g.entryRole", g_id=g_id)
    single = result.single()
    return single[0] if single else None


async def set_entry_role(session: Session, g_id, r_id):
    """ Set the entry-role for the given guild to the given role. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "SET g.entryRole = {r_id}", g_id=g_id, r_id=r_id)


async def remove_entry_role(session: Session, g_id):
    """ Remove the entry-role for the given guild. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "REMOVE g.entryRole", g_id=g_id)


async def get_guilds_with_entry_roles(session):
    """ Return a (g_id, r_id) tuple for each guild that has an entry role. """

    results = await session.run(
        "MATCH (g:Guild)\n"
        "WHERE exists(g.entryRole)\n"
        "RETURN g.id, g.entryRole")
    return results.values()
