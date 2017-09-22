from queue import Queue
import typing
import threading
import discord, RiotAPI, GoogleAPI
from RiotAPI_classes import InGameSummoner

from Sensitive import RIOT_API_KEY, YOUTUBE_API_KEY


class LinkBot:
    def __init__(self):
        # setting this false along with isStopping will terminate the message sending thread.
        self.active = False  # type: bool
        # setting this to true will stop the retrieval of messages, and the program will wait for command threads to terminate.
        self.isStopping = False # type: bool
        # if the bot is not active, but the stop was not requested, the bot will restart.
        self.requestedStop = False # type: bool

        self.encounteredError = False
        self.error = None

        self.messages_to_send = Queue() # type: Queue
        self.messages_received = Queue() # type: Queue
        self.lock = threading.RLock() # type: threading.RLock

        # for each server, there is a list of user ids for registered admins.
        self.admins = dict()
        # for each server, there is a list of tuples containing (name, quote)
        self.quotes = dict()
        # for each server, there is a dictionary of names with a birthday.
        self.birthdays = dict()
        # for each server, there is a bool saying whether the nsfw filter is enabled on that server or not.
        self.nsfw = dict()

        # config settings
        self.owner = None # type: typing.Optional[discord.User]
        self.prefix = 'link.' # type: str

        # other settings
        self.lolgame_region = 'na' # type: str


link_bot = LinkBot()


COMMAND_SYNTAX = {
    'help': '`help [here] [command]`',
    'migrate': '`migrate <channel 1>, <channel 2>`',
    'quote': '`quote <#id>`\t`quote list [author]`\t`quote random [author]`\n'
              '`quote add <quote -author>`\t`quote remove <#id>`',
    'birthday': '`birthday list`\t`birthday set <name> <mm/dd>`\t`birthday remove <name>`',
    'lolgame': '`lolgame <summoner name> [region]`',
    'yt': '`youtube <query>` or `yt <query>`',
    'img': '`image <query>` or `img <query>`',
    'play': '`play`',
    'suggest': '`suggest <feature>`',
    'admin': '`admin list`\t`admin add <@user|@role>`\t`admin remove <@user|@role>`',
    'nsfw': '`nsfw <on|off>`',
    'logout': '`logout` or `logoff`'
}

HELP = '\n' \
       'Argument syntax:  `command`  **mandatory**  *optional*  ***admin only***  __sub command__  option 1/option 2\n' \
       'Command prefix: \'{0}\'\n'\
       'Use "{1}" to get more info on a particular command, for example: help quote\n\n' \
       '-{1}\n-{2}\n-{3}\n-{4}\n-{5}\n-{6}\n-{7}\n-{8}\n-{9}\n-{10}\n-{11}\n-{12}' \
    .format('{0}', COMMAND_SYNTAX['help'], COMMAND_SYNTAX['migrate'], COMMAND_SYNTAX['quote'],
            COMMAND_SYNTAX['birthday'],COMMAND_SYNTAX['lolgame'], COMMAND_SYNTAX['yt'], COMMAND_SYNTAX['img'],
            COMMAND_SYNTAX['play'], COMMAND_SYNTAX['suggest'], COMMAND_SYNTAX['admin'], COMMAND_SYNTAX['nsfw'],
            COMMAND_SYNTAX['logout'])

COMMAND_HELP = {
    "help": "{0}: Pastes help into a DM with the user who sent the command.\n"
            "{prefix}help here\t\t\t\tWrites the help panel to the channel you asked for it in.\n"
            "{prefix}help quote\t\t\t\tGets specific help for the 'quote' command.\n"
            "{prefix}help here quote\t\t\t\tWrites that specific help to the channel you asked for it in."
        .format(COMMAND_SYNTAX["help"], prefix=link_bot.prefix),
    "migrate": "{0}: Moves all members inside voice channel 1 to voice channel 2.\n"
               "{prefix}migrate BK lounge, The Potion Shop\t\t\t\tMoves everyone in the BK Lounge to the Potion Shop.\n"
               "\t\t\t\tIt's not case sensitive, so you could also use:\n"
               "{prefix}migrate bk lounge, the potion shop\t\t\t\tand it would still work with the same effect."
        .format(COMMAND_SYNTAX["migrate"], prefix=link_bot.prefix),
    "quote": "{0}: Get a quote, list them all or add/remove a quote.\n"
              "Adding or removing quote is an Admin Only privilege.\n"
              "{prefix}quote 21\t\t\t\tWrites the quote with an ID of 21. If you don't know the quote ID, use:\n"
              "{prefix}quote list\t\t\t\tLists all quote for the server. You can even filter it for only quote from a particular author:\n"
              "{prefix}quote list LocalIdiot\t\t\t\tThis will show all quote from LocalIdiot.\n"
              "{prefix}quote random\t\t\t\tGets a random quote from the server."
              "{prefix}quote random Jimbob\t\t\t\tgets a random quote from Jimbob."
              "{prefix}quote add Hey, it's me! -Dawson\t\t\t\tThis will add \"Hey, it's me\" as a quote from Dawson.\n"
              "\t\t\t\tYou can separate different parts of a quote using `shift+enter` to start a new line.\n"
              "\t\t\t\tYou still need a quote author at the end, so don't forget!\n"
              "{prefix}quote remove 12\t\t\t\tThis will remove the quote that has an ID of 12. Remember to check '{prefix}quote list' to get the ID!"
        .format(COMMAND_SYNTAX["quote"], prefix=link_bot.prefix),
    "birthday": "{0}: Set, remove, or list the registered birthdays from the database.\n"
                "Setting and removing birthdays is an Admin Only privilege.\n"
                "{prefix}birthday set xCoDGoDx 04/20\t\t\t\tThis will set xCoDGoDx's birthday as April 20th.\n"
                "{prefix}birthday list\t\t\t\twill list all birthdays that are registered for this server.\n"
                "{prefix}birthday remove xCoDGoDx\t\t\t\twill remove xCoDGoDx's birthday from the system."
        .format(COMMAND_SYNTAX["birthday"], prefix=link_bot.prefix),
    "lolgame": "{0}: Sends info to the channel about `summoner`'s current League of Legends game.\n"
               "{prefix}lolgame TheBootyToucher\t\t\t\tLooks up and posts information in the chat about TheBootyToucher's league of legends game.\n"
               "\t\t\t\tSummoner names are not case-sensitive, and they also do not require you to use spaces in the name. Therefore:\n"
               "{prefix}lolgame thebootytoucher\t\t\t\twill correctly retrieve the player's info, even if his name is something like, 'ThE BoOtY tOuChEr'.\n"
               "{prefix}lolgame thebootytoucher, kr\t\t\t\tWill look on the Korean servers for the player's game. You can specify any region, but you'll need to know the region ID yourself."
        .format(COMMAND_SYNTAX["lolgame"], prefix=link_bot.prefix),
    "yt": "{0}: Links the first video result of a YouTube search for `query`\n"
          "{prefix}youtube the dirtiest of dogs\t\t\t\tThis will link the first youtube video found in the search results for 'the dirtiest of dogs'.\n"
          "{prefix}yt why did i do that\t\t\t\tYou can also use just 'yt' instead of typing out 'youtube'."
        .format(COMMAND_SYNTAX["yt"], prefix=link_bot.prefix),
    "img": "{0}: Links the first image result of a Google Image search for `query`.\n"
           "{prefix}image what blind people see\t\t\t\tLinks the first result of a google image search for 'what blind people see'.\n"
           "{prefix}img i don't know what i expected\t\t\t\tYou can also use simply 'img' instead of typing out 'image'."
        .format(COMMAND_SYNTAX["img"], prefix=link_bot.prefix),
    "play": "{0}: Plays something in voice chat with you!"
        .format(COMMAND_SYNTAX["play"]),
    "suggest": "{0}: Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.\n"
               "{prefix}suggest Flying puppies please!\t\t\t\tThis will leave a suggestion for flying puppies - politely..."
        .format(COMMAND_SYNTAX["suggest"], prefix=link_bot.prefix),
    "admin": "{0}: List admins, or add/remove them, but only admins or the bot owner can add/remove admins.\n"
             "{prefix}admin list\t\t\t\tThis will list all of the admins for this server.\n"
             "{prefix}admin add @JoeBlow\t\t\t\tWill add JoeBlow as an admin. This has to be a valid mention too!\n"
             "{prefix}admin add @TheBigDawgs\t\t\t\tIf TheBigDawgs is a role, this will add all members of TheBigDawgs as admins. Convenience!\n"
             "\t\t\t\tSpeaking of convenience, you can also chain your mentions together to add multiple people and/or roles as admins:\n"
             "{prefix}admin add @JoeBlow @JoeShmoe @JohnDoe @TheBigDawgs @TheSmallDawgs\n"
             "{prefix}admin remove @JoeBlow @TheBigDawgs\t\t\t\tRemoving admins works the same way."
        .format(COMMAND_SYNTAX["admin"], prefix=link_bot.prefix),
    "nsfw": "{0}: View the state of the NSFW filter, or **Admin Only** turn it `on` or `off`.\n"
            "\t\t\t\t\tCurrently, it is always disabled due to a bug with Google's API."
        .format(COMMAND_SYNTAX["nsfw"]),
    "logout": "{0}: **Owner Only** Logs the bot out."
        .format(COMMAND_SYNTAX["logout"])
}


client = discord.Client()
riot_api = RiotAPI.Client(RIOT_API_KEY)
google_api = GoogleAPI.Client(YOUTUBE_API_KEY)


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


def FormatAsColumn(append, column_length):
    """
    Returns the append string with spaces added to create a column format.

    :param append: String of text to be formatted.
    :type append: str
    :param column_length: Number of characters in this column.
    :type column_length: int
    :return: The newly formatted string.
    :rtype: str
    """
    add_spaces = column_length - len(append)
    while add_spaces > 0:
        append += ' '
        add_spaces -= 1
    return append


def FormatAsLoLPlayerOutput(player):
    """
    Formats a player's in-game information into columns for outputting in monospace.

    :param player: The player whose output should be formatted.
    :type player: InGameSummoner
    :return: A string with the formatting applied.
    :rtype: str
    """
    string = FormatAsColumn(player.summoner.name, 17) \
             + FormatAsColumn(player.rank, 15) \
             + FormatAsColumn(str(player.lp), 6) \
             + FormatAsColumn(player.series, 6) \
             + FormatAsColumn(player.champion.idealized, 15) \
             + FormatAsColumn(str(player.games_champ), 6) \
             + FormatAsColumn(str(player.win_rate_champ) + '%', 5) \
             + FormatAsColumn(str(player.kda_champ), 6) \
             + FormatAsColumn(str(player.games), 6) \
             + FormatAsColumn(str(player.win_rate) + '%', 8) \
             + FormatAsColumn(str(player.kda), 5) \
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
    if member.server.id not in link_bot.admins.keys():
        link_bot.admins[member.server.id] = list()
        return False
    return member.id in link_bot.admins[member.server.id]


def IsOwner(user):
    """
    Checks if the user is the bot's owner.

    :param discord.User user:
    :return: True if the user is the bot's owner, False otherwise.
    :rtype: bool
    """
    return user.id == link_bot.owner.id