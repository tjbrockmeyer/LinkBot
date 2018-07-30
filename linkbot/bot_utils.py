
from linkbot.bot import bot
from utils import emoji
import utils.database as db


def is_admin(member):
    """
    Checks if the member is an admin.

    :param discord.Member member: Member to check if they're an admin.
    :return: True if the member is an admin, False otherwise.
    :rtype: bool
    """
    if is_owner(member):
        return True
    with db.connect() as (conn, cur):
        cur.execute(
            """
            SELECT user_id FROM admins
            WHERE server_id = %s AND user_id = %s;
            """, [member.guild.id, member.id])
        if cur.fetchone() is not None:
            return True
    return False

def is_owner(user):
    """
    Checks if the user is the bot's owner.

    :param discord.User user:
    :return: True if the user is the bot's owner, False otherwise.
    :rtype: bool
    """
    return user == bot.owner


async def send_success(message):
    await message.add_reaction(emoji=emoji.checkmark)
