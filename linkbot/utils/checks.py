from typing import Union

import discord

import linkbot.utils.queries.admin as admin
import neo4jdb as db
from linkbot.bot import bot


async def is_admin(member: discord.Member):
    """ Checks if the member is able to use admin commands. This can be an Admin, Bot owner, or Server owner. """
    if is_bot_owner(member) or is_server_owner(member):
        return True
    async with await db.Session.new() as sess:
        if await admin.get_member_is_admin(sess, member.guild.id, member.id):
            return True
    return False


def is_bot_owner(user: Union[discord.Member, discord.User]):
    """ Checks if the user is the owner of the bot. """
    return user == bot.owner


def is_server_owner(member: discord.Member):
    """ Checks if the member owns the server. """
    return member.guild.owner == member
