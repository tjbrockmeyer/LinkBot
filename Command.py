from CommandFuncs import *

from CommandInfo import COMMANDS


class Command:
    """
    A parsed message that looks for the prefix, a command, and args following the command.

    :var self.message: The message that was sent.
    :var self.author: The user/member who sent the message.
    :var self.channel: The channel that the command was sent in.
    :var self.server: The server that the command was issued on. None if the channel is private.

    :var self.hasPrefix: Whether or not the prefix was attached to the beginning of the message.
    :var self.command: The command that was sent.
    :var self.argstr: The string proceeding the command.
    :var self.args: A list of strings that proceeded the command. All whitespace has been removed.

    :var self.info: A dictionary of info for this command. None if the command doesn't exist.
    :var self.isValid: A bool stating whether this is a valid command or not.

    :var self.loop: The asyncio event loop to be used for threadsafe coroutimes.
    """

    def __init__(self, message):
        """
        Parse a message into an attempted command.

        :param message: The message to parse.
        :type message: discord.Message
        :param loop: The asyncio event loop to be used for coroutine calls.
        :type loop: asyncio.EventLoop
        """

        # Get channel and server
        self.channel = message.channel
        if self.channel.is_private:
            self.server = None
        else:
            self.server = message.channel.server

        # Get message and author
        self.author = message.author
        self.message = message

        # Get arg string and prefix
        self.argstr = message.content
        self.hasPrefix = message.content.startswith(link_bot.prefix)
        if self.hasPrefix:
            self.argstr = self.argstr[len(link_bot.prefix):].lstrip()

        # Get command.
        try:
            self.command = self.argstr[:self.argstr.index(' ')]
        except ValueError:
            self.command = self.argstr

        # Get args
        self.argstr = self.argstr[len(self.command):].lstrip()
        tempargs = self.argstr.split(' ')
        self.args = []
        for x in tempargs:
            x = x.strip()
            if x != '':
                self.args.append(x)

        # Get info
        self.info = Command.GetCommandInfo(self.command.lower())
        self.isValid = self.info is not None


    def OnSyntaxError(self, info):
        SendMessage(self.channel, OnSyntaxError(self.command, info))


    @staticmethod
    def GetHelp(cmdstr):
        info = Command.GetCommandInfo(cmdstr)
        if info is None:
            return None
        return info['help'].format(syntax=info['syntax'], prefix=link_bot.prefix)


    @staticmethod
    def GetCommandInfo(cmdstr):
        """
        Gets the dict within the COMMANDS dict that belongs to this command. Follows aliases.

        :param cmdstr: Command name as a string.
        :type cmdstr: str
        :return: The dict containing 'func', 'syntax', and 'help' for cmd. Returns None if cmd was not found.
        :rtype: dict
        """
        if cmdstr in COMMANDS:
            if 'alias' in COMMANDS[cmdstr]:
                return Command.GetCommandInfo(COMMANDS[cmdstr]['alias'])
            return COMMANDS[cmdstr]
        return None

    @staticmethod
    def EnumerateCommands_abc():
        # get a sorted list of all commands that are not aliases
        commands = [x for x in COMMANDS if 'alias' not in COMMANDS[x]]
        for cmd in sorted(commands):
            yield cmd, COMMANDS[cmd]