import asyncio
import logging
import threading

import discord

from Main.Bot import link_bot


def SafeCommandFunc(cmd):
    try:
        cmd.info.func(cmd)
    except Exception as e:
        SendErrorMessage("Exception occurred in {}: {}".format(cmd.info.func, e))


# runs commandFunc on a new thread, passing it message and argstr. name becomes the name of the thread.
def RunCommand(cmd):
    cmd.loop = asyncio.get_event_loop()
    commandThread = threading.Thread(name='cmd_' + cmd.command, target=SafeCommandFunc, args=(cmd,))
    commandThread.start()


# adds a message that is to be sent to the message queue. The message is then sent by the send message thread.
def SendMessage(destination, message='', embed=None):
    link_bot.messages_to_send.put((destination, message, embed))


# sends a message the the owner containing details on some error. Does nothing if there is no owner.
def SendErrorMessage(message: str):
    if link_bot.owner is not None:
        SendMessage(link_bot.owner, message)
    logging.error(message)


def OnSyntaxError(command: str, info: str) -> str:
    """
    To be called when there has been a syntax error in a command.
    Returns info and command formatted into a help string.

    :param command: The command that received a syntax error.
    :type command: str
    :param info: Some info as to what went wrong with the syntax.
    :type info: str
    :return: A new string with the parameters formatted in.
    :rtype: str
    """
    return "{info} Try `{prefix}help {cmd}` for help on how to use {cmd}."\
        .format(prefix=link_bot.prefix, cmd=command, info=info)


def FormatAsNoSpaces(string):
    """
    Returns the same string, but with no spaces in it.

    :param string: The string to remove spaces from.
    :type string: str
    :return: The string with no spaces.
    :rtype: str
    """
    return ''.join(string.split())


def FormatAsColumn(content, column_length, alignment=-1):
    """
    Returns the append string with spaces added to create a column format.

    :param alignment: The alignment of the content in the column. -1 for left, 0 for center, 1 for right.
    :type alignment: int
    :param content: String of text to be formatted.
    :type content: str
    :param column_length: Number of characters in this column.
    :type column_length: int
    :return: The newly formatted string.
    :rtype: str
    """
    add_spaces = column_length - len(content)
    if alignment == 0:
        left = add_spaces // 2
        right = add_spaces - left
        return " " * left + content + " " * right
    if alignment < 0:
        return content + " " * add_spaces
    return " " * add_spaces + content


def FormatAsLoLPlayerOutput(player):
    """
    Formats a player's in-game information into columns for outputting in monospace.

    :param player: The player whose output should be formatted.
    :type player: InGameSummoner
    :return: A string with the formatting applied.
    :rtype: str
    """
    string = FormatAsColumn(player.summoner.name, 17, alignment=1) \
             + FormatAsColumn(player.rank, 15, alignment=0) \
             + FormatAsColumn(str(player.lp), 6, alignment=-1) \
             + FormatAsColumn(player.series, 6, alignment=0) \
             + FormatAsColumn(player.champion.idealized, 15, alignment=0) \
             + FormatAsColumn(str(player.games_champ), 6, alignment=-1) \
             + FormatAsColumn(str(player.win_rate_champ) + '%', 5, alignment=1) \
             + FormatAsColumn(str(player.kda_champ), 6, alignment=-1) \
             + FormatAsColumn(str(player.games), 6, alignment=-1) \
             + FormatAsColumn(str(player.win_rate) + '%', 8, alignment=1) \
             + FormatAsColumn(str(player.kda), 5, alignment=-1) \
             + '\n'
    return string


def IsAdmin(member):
    """
    Checks if the member is an admin.

    :param discord.Member member: Member to check if they're an admin.
    :return: True if the member is an admin, False otherwise.
    :rtype: bool
    """
    if IsOwner(member):
        return True
    if member.server.id not in link_bot.data:
        return False
    if 'admins' not in link_bot.data[member.server.id]:
        return False
    return member.id in link_bot.data[member.server.id]['admins']


def IsOwner(user):
    """
    Checks if the user is the bot's owner.

    :param discord.User user:
    :return: True if the user is the bot's owner, False otherwise.
    :rtype: bool
    """
    return user.id == link_bot.owner.id