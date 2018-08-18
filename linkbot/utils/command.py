
from functools import reduce
import discord
import linkbot.utils.database as db


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
    """

    def __init__(self, bot, message: discord.Message):
        """
        Parse a message into an attempted command.

        :param message: The message to parse.
        :type message: discord.Message
        """
        self.bot_prefix = bot.prefix

        # Get channel and server
        self.channel = message.channel
        if isinstance(self.channel, discord.TextChannel):
            self.guild = message.channel.guild
        else:
            self.guild = None

        # Get message and author
        self.author = message.author
        self.message = message
        self.is_dm = isinstance(self.channel, discord.DMChannel)

        # Get arg string and prefix
        self.argstr = message.content
        self.has_prefix = message.content.startswith(bot.prefix)
        if self.has_prefix:
            self.argstr = self.argstr[len(bot.prefix):].lstrip()

        # Get command.
        try:
            self.command_arg = self.argstr[:self.argstr.index(' ')]
        except ValueError:
            self.command_arg = self.argstr

        # Get args
        self.argstr = self.argstr[len(self.command_arg):].lstrip()
        tempargs = self.argstr.split(' ')
        self.args = []
        for x in tempargs:
            x = x.strip()
            if x != '':
                self.args.append(x)

        # Get info
        self.info: CommandInfo = bot.commands.get(self.command_arg.lower())
        self.is_valid = self.info is not None

    def is_banned(self):
        if not self.is_valid:
            return False
        with db.connect() as (conn, cur):
            cur.execute("SELECT command FROM cmdbans WHERE server_id = %s AND user_id = %s AND command = %s;",
                        [self.guild.id, self.author.id, self.info.command])
            return cur.fetchone() is not None

    async def run(self):
        await self.info.func(self)

    def shiftargs(self, count=1):
        while count > 0 and len(self.args) > 0:
            self.argstr = self.argstr[len(self.args[0]):].lstrip()
            self.args = self.args[1:]
            count -= 1


class CmdExample:
    """
    Holds an example use of a command and its corresponding effect.

    :cmd: (str) The example use of the command.
    :effect: (str) The descriptive effect of the example.
    """
    def __init__(self, cmd, effect):
        self.cmd = cmd
        self.effect = effect


class CommandInfo:
    """ Class containing info about a particular command. """
    def __init__(self, name, func, syntax, description, examples, aliases, show_in_help):
        self.command = name
        self.func = func
        self.syntax = syntax
        self.description = description
        self.examples = [CmdExample(cmd, effect) for (cmd, effect) in examples]
        self.aliases = aliases
        self.show_in_help = show_in_help

    def get_syntax_with_format(self, prefix, mk_down='`', sep=' || '):
        """
        Formats the syntax of this command using the args.

        :param str prefix: The command prefix for the bot.
        :param str mk_down: The markdown string that should be placed on both sides of the syntax.
        :param str sep: The string that will seperate each syntax case.
        :return: The syntax cases formatted according to the parameters.
        """
        fn = lambda full, syn: full + "{sep}{mk}{syn}{mk}".format(sep=sep, mk=mk_down,
                                                                  syn=syn.format(c=prefix + self.command))
        return reduce(fn, self.syntax, '')[len(sep):]

    def get_examples_with_format(self, prefix, cmd_as_code=True, cmd_ex_sep='\n\t', sep='\n'):
        """
        Formats the examples for this command using the args provided.

        :param str prefix: The command prefix for the bot.
        :param bool cmd_as_code: Format the command portion of the example as a code snippet?
        :param str cmd_ex_sep: The separating string between the command and effect portions of the example.
        :param str sep: The separating string between examples.
        :return: A string of the formatted examples.
        """
        fn = lambda full, ex: full + "{sep}{tick}{cmd}{tick}{ex_sep}{effect}"\
            .format(sep=sep, tick='`' if cmd_as_code else '', cmd=ex.cmd, ex_sep=cmd_ex_sep, effect=ex.effect)
        return reduce(fn, self.examples, '')[len(sep):].format(prefix=prefix)

    def embed_syntax(self, embed, prefix, mk_down='`', title_mk_down='', sep=' || ', inline=False):
        """
        Embeds the syntax of this command into the passed embed as a new field.

        :param str prefix: The command prefix for the bot.
        :param discord.Embed embed: The embed to create a new field on.
        :param str mk_down: The markdown string to be placed on both sides of the syntax.
        :param str title_mk_down: The markdown string to be placed on both sides of the title.
        :param str sep: String to be used to separate the syntax cases.
        :param bool inline: Should this embed be created inline?
        """
        embed.add_field(
            name="{mk}{cmd}{mk}".format(cmd=' | '.join([self.command] + self.aliases), mk=title_mk_down),
            value=self.get_syntax_with_format(prefix, mk_down, sep), inline=inline)

    def embed_examples(self, embed, prefix, cmd_as_code=True):
        """
        Embeds the examples for this command into the passed embed as new fields.

        :param str prefix: The command prefix for the bot.
        :param discord.Embed embed: The embed to create a new field on.
        :param bool cmd_as_code: Should each command portion be shown as a code snippet?
        """
        for ex in self.examples:
            embed.add_field(name="{mk}{cmd}{mk}"
                            .format(cmd=ex.cmd.format(c=prefix + self.command),
                                    mk='`' if cmd_as_code else ''), value=ex.effect, inline=False)
