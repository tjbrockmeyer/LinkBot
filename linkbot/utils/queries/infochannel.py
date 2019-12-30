from neo4jdb import Session


async def set_info_channel(session: Session, g_id, c_id):
    """ Set the info channel of the given guild to the given channel. """

    await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "SET g.infoChannel = {c_id}", g_id=g_id, c_id=c_id)


async def get_info_channel(session: Session, g_id):
    """ Return the channel id of the designated info channel for the given guild.
        Return the system channel if no channel has been specified. """

    result = await session.run(
        "MATCH (g:Guild {id: {g_id}})\n"
        "WHERE exists(g.infoChannel)\n"
        "RETURN g.infoChannel", g_id=g_id)
    result = result.single()
    return result[0] if result else None
