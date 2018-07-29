
from linkbot.bot import bot
from utils import emoji


def is_admin(member):
    """
    Checks if the member is an admin.

    :param discord.Member member: Member to check if they're an admin.
    :return: True if the member is an admin, False otherwise.
    :rtype: bool
    """
    if is_owner(member):
        return True
    if member.server.id not in bot.data:
        return False
    if 'admins' not in bot.data[member.server.id]:
        return False
    return member.id in bot.data[member.server.id]['admins']

def is_owner(user):
    """
    Checks if the user is the bot's owner.

    :param discord.User user:
    :return: True if the user is the bot's owner, False otherwise.
    :rtype: bool
    """
    return user.id == bot.owner.id


async def send_success(message):
    await message.add_reaction(emoji=emoji.checkmark)
