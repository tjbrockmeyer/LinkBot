from functools import reduce

from Main.LinkBot import bot


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
    """
    Class containing info about a particular command.

    :func: (function) The function that this command calls.
    :syntax: (list[str]) A list of syntax cases
    :description: (str) A description of the function of this command.
    :examples: (list[CmdExample]) A list of examples.
    """
    def __init__(self, name, func, syntax, description, examples, aliases, show_in_help):
        self.command = name
        self.func = func
        self.syntax = [s.format(c=(bot.prefix + name)) for s in syntax]
        self.description = description
        self.examples = [CmdExample(cmd.format(c=(bot.prefix + name)), effect) for (cmd, effect) in examples]
        self.aliases = aliases
        self.show_in_help = show_in_help

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
            name="{mk}{cmd}{mk}".format(cmd=' | '.join([self.command] + self.aliases), mk=title_mk_down),
            value=self.get_syntax_with_format(mk_down, sep), inline=inline)

    def embed_examples(self, embed, cmd_as_code=True):
        """
        Embeds the examples for this command into the passed embed as new fields.

        :param discord.Embed embed: The embed to create a new field on.
        :param bool cmd_as_code: Should each command portion be shown as a code snippet?
        """
        for ex in self.examples:
            embed.add_field(name="{mk}{cmd}{mk}"
                            .format(cmd=ex.cmd.format(prefix=bot.prefix),
                                    mk='`' if cmd_as_code else ''), value=ex.effect, inline=True)
