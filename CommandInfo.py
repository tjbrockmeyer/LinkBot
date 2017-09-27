from CommandFuncs import *
from functools import reduce


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

    def GetSyntaxWithFormat(self, mk_down='`', sep=' || '):
        """
        Formats the syntax of this command using the args.

        :param str mk_down: The markdown string that should be placed on both sides of the syntax.
        :param str sep: The string that will seperate each syntax case.
        :return: The syntax cases formatted according to the parameters.
        :rtype: str
        """
        fn = lambda x, y: x + "{sep}{mk}{syn}{mk}".format(sep=sep, mk=mk_down, syn=y)
        return reduce(fn, self.syntax, '')[len(sep):]

    def GetExamplesWithFormat(self, cmd_as_code=True, cmd_ex_sep='\n\t', sep='\n'):
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
        return reduce(fn, self.examples, '')[len(sep):].format(prefix=link_bot.prefix)

    def EmbedSyntax(self, embed, mk_down='`', title_mk_down='', sep=' || ', inline=False):
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
            value=self.GetSyntaxWithFormat(mk_down, sep), inline=inline)

    def EmbedExamples(self, embed, cmd_as_code=True):
        """
        Embeds the examples for this command into the passed embed as new fields.

        :param discord.Embed embed: The embed to create a new field on.
        :param bool cmd_as_code: Should each command portion be shown as a code snippet?
        """
        for ex in self.examples:
            embed.add_field(name="{tick}{cmd}{tick}"
                            .format(cmd=ex.cmd.format(prefix=link_bot.prefix),
                                    tick='`' if cmd_as_code else ''), value=ex.effect, inline=True)


def IsCommand(cmdstr):
    """
    Returns true if the passed command string is a valid command.

    :param cmdstr: Command to check validity of.
    :type cmdstr: str
    :return: True if the command is valid, False otherwise.
    :rtype: bool
    """
    return cmdstr in COMMANDS


def GetCommandInfo(cmdstr):
    """
    Gets the CommandInfo within the COMMANDS dict that belongs to this command. Follows aliases.

    :param cmdstr: Command name as a string.
    :type cmdstr: str
    :return: The CommandInfo containing 'func', 'syntax', and 'help' for cmd. Returns None if cmd was not found.
    :rtype: CommandInfo
    """
    if cmdstr in COMMANDS:
        if 'alias' in COMMANDS[cmdstr]:
            return GetCommandInfo(COMMANDS[cmdstr]['alias'])
        return CommandInfo(cmdstr)
    return None


def EnumerateCommands_abc():
    """
    Enumerates the list of commands in alphabetical order.

    :return: A tuple of (commandString, CommandInfo for commandString)
    :rtype: str, CommandInfo
    """
    # get a sorted list of all commands that are not aliases
    commands = [x for x in COMMANDS if 'alias' not in COMMANDS[x]]
    for cmd in sorted(commands):
        yield CommandInfo(cmd)


COMMANDS = {
    'help': {
        'func': cmd_help,
        'syntax': ["help [here] [command]"],
        'description': "Pastes help into a DM with the user who sent the command.",
        'examples': [
            {'command': "{prefix}help here",
            'effect': "Writes the help panel to the channel you asked for it in."},
            {'command': "{prefix}help quote",
            'effect': "Gets specific help for the 'quote' command."},
            {'command': "{prefix}help here quote",
            'effect': "Writes that specific help to the channel you asked for it in."}
        ]
    },
    'migrate': {
        'func': cmd_migrate,
        'syntax': ["migrate <ch>, <ch>"],
        'description': "Moves all members inside voice channel 1 to voice channel 2.",
        'examples': [
            {'command': "{prefix}migrate BK lounge, The Potion Shop",
            'effect': "Moves everyone in the BK Lounge to the Potion Shop."},
            {'command': "{prefix}migrate bk lounge, the potion shop",
            'effect': "It's not case sensitive, so this would still work with the same effect."}
        ]
    },
    'quote': {
        'func': cmd_quote,
        'syntax': ["quote <#id>", "quote list [author]", "quote random [author]",
                    "quote add <quote -author>", "quote remove <#id>"],
        'description': "Get a quote, list them all or add/remove a quote.",
        'examples': [
            {'command': "{prefix}quote 21",
            'effect': "Writes the quote with an ID of 21. If you don't know the quote ID, use:"},
            {'command': "{prefix}quote list",
            'effect': "Lists all quote for the server. You can even filter it for only quotes from a particular author:"},
            {'command': "{prefix}quote list LocalIdiot",
            'effect': "This will show all quotes from LocalIdiot."},
            {'command': "{prefix}quote random",
            'effect': "Gets a random quote from the server."},
            {'command': "{prefix}quote random Jimbob",
            'effect': "gets a random quote from Jimbob."},
            {'command': "{prefix}quote add Hey, it's me! -Dawson",
            'effect': "This will add \"Hey, it's me\" as a quote from Dawson."},
            {'command': "{prefix}quote add Anyone: Hey Daws.\nDawson: Seeya!",
            'effect': "You can separate different parts of a quote using a new line (shift+enter)."},
            {'command': "{prefix}quote remove 12",
            'effect': "This will remove the quote that has an ID of 12. Remember to check 'quote list' to get the ID!"}
        ]
    },
    'birthday': {
        'func': cmd_birthday,
        'syntax': ["birthday list", "birthday set <name> <mm/dd>", "birthday remove <name>"],
        'description': "Set, remove, or list the registered birthdays from the database.",
        'examples': [
            {'command': "{prefix}birthday set xCoDGoDx 04/20",
            'effect': "This will set xCoDGoDx's birthday as April 20th."},
            {'command': "{prefix}birthday list",
            'effect': "will list all birthdays that are registered for this server."},
            {'command': "{prefix}birthday remove xCoDGoDx",
            'effect': "will remove xCoDGoDx's birthday from the system."}
        ]
    },
    'lolgame': {
        'func': cmd_lolgame,
        'syntax': ["lolgame <player> [region]"],
        'description': "Sends info to the channel about `summoner`'s current League of Legends game.",
        'examples': [
            {'command': "{prefix}lolgame The Booty Toucher",
            'effect': "Looks up and posts information in the chat about The Booty Toucher's league of legends game."},
            {'command': "{prefix}lolgame thebootytoucher",
            'effect': "Summoner names are not case sensitive, nor are the spaces mandatory."},
            {'command': "{prefix}lolgame thebootytoucher, kr",
            'effect': "Will look on the Korean servers for the player's game. You can specify any region, but you'll need to know the region ID yourself."}
        ]
    },
    'yt': {
        'alias': 'youtube'
    },
    'youtube': {
        'func': cmd_youtube,
        'syntax': ["youtube <query>", "yt <query>"],
        'description': "Links the first video result of a YouTube search for query",
        'examples': [
            {'command': "{prefix}youtube the dirtiest of dogs",
            'effect': "This will link the first youtube video found in the search results for 'the dirtiest of dogs'."},
            {'command': "{prefix}yt why did i do that",
            'effect': "You can also use just 'yt' instead of typing out 'youtube'."}
        ]
    },
    'img': {
        'alias': 'image'
    },
    'image': {
        'func': cmd_image,
        'syntax': ["image <query>", "img <query>"],
        'description': "Links the first image result of a Google Image search for `query`.",
        'examples': [
            {'command': "{prefix}image what blind people see",
            'effect': "Links the first result of a google image search for 'what blind people see'."},
            {'command': "{prefix}img i don't know what i expected",
            'effect': "You can also use simply 'img' instead of typing out 'image'."}
        ]
    },
    'play': {
        'func': cmd_play,
        'syntax': ["play"],
        'description': "Plays something in voice chat with you!",
        'examples': [
            {'command': "{prefix}play",
            'effect': "Bot joins the voice channel with you."}
        ]
    },
    'suggest': {
        'func': cmd_suggest,
        'syntax': ["suggest <feature>"],
        'description': "Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.",
        'examples': [
            {'command': "{prefix}suggest Flying puppies please!",
             'effect': "Leaves a suggestion for flying puppies - politely..."}
        ]
    },
    'nsfw': {
        'func': cmd_nsfw,
        'syntax': ["nsfw <on|off>"],
        'description': "View the state of the NSFW filter, turn it on/off.",
        'examples': [
            {'command': "{prefix}nsfw on",
             'effect': "Turns on the NSFW filter for this server."}
        ]
    },
    'unpause': {
        'alias': 'pause'
    },
    'pause': {
        'func': cmd_pause,
        'syntax': ["pause", "unpause"],
        'description': "Pause or unpause the bot. Pausing will prevent the bot from receiving commands until unpaused.",
        'examples': [
            {'command': "{prefix}pause",
             'effect': "Pauses the bot, preventing command processing."},
            {'command': "{prefix}unpause",
             'effect': "Unpauses the bot, allowing commands to be processed."}
        ]
    },
    'admin': {
        'func': cmd_admin,
        'syntax': ["admin list", "admin add <@user|@role>", "admin remove <@user|@role>"],
        'description': "List admins, or add/remove them.",
        'examples': [
            {'command': "{prefix}admin list",
            'effect': "Lists all of the admins for this server."},
            {'command': "{prefix}admin add @JoeBlow",
            'effect': "Adds JoeBlow as an admin. This has to be a valid mention!"},
            {'command': "{prefix}admin add @TheBigDawgs",
            'effect': "If TheBigDawgs is a role, adds all members of TheBigDawgs as admins."},
            {'command': "{prefix}admin add @JoeBlow @TheBigDawgs",
            'effect': "Chain mentions together to add multiple people and/or roles as admins"},
            {'command': "{prefix}admin remove @JoeBlow @TheBigDawgs",
            'effect': "Removing admins works the same way."}
        ]
    },
    'logoff': {
        'alias': 'logout'
    },
    'logout': {
        'func': cmd_logout,
        'syntax': ["logout", "logoff"],
        'description': "**Owner Only** Logs the bot out.",
        'examples': [
            {'command': "{prefix}logout",
            'effect': "Logs the bot out."}
        ]
    }
}