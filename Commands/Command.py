from Main.Bot import link_bot
from Main.Helper import SendMessage, OnSyntaxError
import discord


class Command:
    """
    A parsed message that looks for the prefix, a command, and args following the command.

    :message: (discord.Message) The message that was sent.
    :author: (discord.User/discord.Member) The user/member who sent the message.
    :channel: (discord.Channel) The channel that the command was sent in.
    :server: [discord.Server] The server that the command was issued on. None if the channel is private.

    :hasPrefix: (bool) Whether or not the prefix was attached to the beginning of the message.
    :command: (str) The command that was sent.
    :argstr: (str) The string proceeding the command.
    :args: (list[str]) A list of strings that proceeded the command. All whitespace has been removed.

    :info: (CommandInfo) A dictionary of info for this command. None if the command doesn't exist.
    :isValid: (bool) A bool stating whether this is a valid command or not.

    :loop: The asyncio event loop to be used for threadsafe coroutines.
    """

    def __init__(self, message: discord.Message):
        """
        Parse a message into an attempted command.

        :param message: The message to parse.
        :type message: discord.Message
        """
        from Commands.CommandInfo import CommandInfo

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
        self.info = CommandInfo.GetCommandInfo(self.command.lower())
        self.isValid = self.info is not None


    def OnSyntaxError(self, info):
        SendMessage(self.channel, OnSyntaxError(self.command, info))