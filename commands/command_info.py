from functools import reduce


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
                                    mk='`' if cmd_as_code else ''), value=ex.effect, inline=True)
