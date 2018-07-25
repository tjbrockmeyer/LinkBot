from functools import reduce

from Commands.Data import COMMANDS
from Main.LinkBot import bot


class CmdExample:
    """
    Holds an example use of a command and its corresponding effect.

    :cmd: (str) The example use of the command.
    :effect: (str) The descriptive effect of the example.
    """
    def __init__(self, ex):
        self.cmd = ex['command']
        self.effect = ex['effect']


class CommandInfo:
    """
    Class containing info about a particular command.

    :func: (function) The function that this command calls.
    :syntax: (list[str]) A list of syntax cases
    :description: (str) A description of the function of this command.
    :examples: (list[CmdExample]) A list of examples.
    """
    def __init__(self, cmd):
        self.command = cmd
        cmd_dict = COMMANDS[cmd]
        self.func = cmd_dict['func']
        self.syntax = cmd_dict['syntax']
        self.description = cmd_dict['description']
        self.examples = [CmdExample(ex) for ex in cmd_dict['examples']]

    def get_syntax_with_format(self, mk_down='`', sep=' || '):
        """
        Formats the syntax of this command using the args.

        :param str mk_down: The markdown string that should be placed on both sides of the syntax.
        :param str sep: The string that will seperate each syntax case.
        :return: The syntax cases formatted according to the parameters.
        :rtype: str
        """
        fn = lambda x, y: x + "{sep}{mk}{syn}{mk}".format(sep=sep, mk=mk_down, syn=y)
        return reduce(fn, self.syntax, '')[len(sep):]

    def get_examples_with_format(self, cmd_as_code=True, cmd_ex_sep='\n\t', sep='\n'):
        """
        Formats the examples for this command using the args provided.

        :param cmd_as_code: Format the command portion of the example as a code snippet?
        :type cmd_as_code: bool
        :param cmd_ex_sep: The separating string between the command and effect portions of the example.
        :type cmd_ex_sep: str
        :param sep: The separating string between examples.
        :type sep: str
        :return: A string of the formatted examples.
        :rtype: str
        """
        fn = lambda x, y: x + "{sep}{tick}{ex}{tick}{ex_sep}{effect}"\
            .format(sep=sep, tick='`' if cmd_as_code else '', ex=y.cmd, ex_sep=cmd_ex_sep, effect=y.effect)
        return reduce(fn, self.examples, '')[len(sep):].format(prefix=bot.prefix)

    def embed_syntax(self, embed, mk_down='`', title_mk_down='', sep=' || ', inline=False):
        """
        Embeds the syntax of this command into the passed embed as a new field.

        :param discord.Embed embed: The embed to create a new field on.
        :param str mk_down: The markdown string to be placed on both sides of the syntax.
        :param str title_mk_down: The markdown string to be placed on both sides of the title.
        :param str sep: String to be used to separate the syntax cases.
        :param bool inline: Should this embed be created inline?
        """
        embed.add_field(
            name="{mk}{cmd}{mk}".format(cmd=self.command, mk=title_mk_down),
            value=self.get_syntax_with_format(mk_down, sep), inline=inline)

    def embed_examples(self, embed, cmd_as_code=True):
        """
        Embeds the examples for this command into the passed embed as new fields.

        :param discord.Embed embed: The embed to create a new field on.
        :param bool cmd_as_code: Should each command portion be shown as a code snippet?
        """
        for ex in self.examples:
            embed.add_field(name="{tick}{cmd}{tick}"
                            .format(cmd=ex.cmd.format(prefix=bot.prefix),
                                    tick='`' if cmd_as_code else ''), value=ex.effect, inline=True)

    @staticmethod
    def is_command(cmdstr):
        """
        Returns true if the passed command string is a valid command.

        :param cmdstr: Command to check validity of.
        :type cmdstr: str
        :return: True if the command is valid, False otherwise.
        :rtype: bool
        """
        return cmdstr in COMMANDS


    @staticmethod
    def get_command_info(cmdstr):
        """
        Gets the CommandInfo within the COMMANDS dict that belongs to this command. Follows aliases.

        :param cmdstr: Command name as a string.
        :type cmdstr: str
        :return: The CommandInfo containing 'func', 'syntax', and 'help' for cmd. Returns None if cmd was not found.
        :rtype: CommandInfo
        """
        if cmdstr in COMMANDS:
            if 'alias' in COMMANDS[cmdstr]:
                return CommandInfo.get_command_info(COMMANDS[cmdstr]['alias'])
            return CommandInfo(cmdstr)
        return None


    @staticmethod
    def enumerate_commands_abc():
        """
        Enumerates the list of commands in alphabetical order.

        :return: A tuple of (commandString, CommandInfo for commandString)
        :rtype: str, CommandInfo
        """
        # get a sorted list of all commands that are not aliases
        commands = [x for x in COMMANDS if 'alias' not in COMMANDS[x]]
        for cmd in sorted(commands):
            yield CommandInfo(cmd)