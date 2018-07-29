import os
import sys
import logging
import asyncio
import discord
import traceback
from functools import wraps
from importlib import import_module

from utils.funcs import load_json, create_config
from utils.IniIO import IniIO
from linkbot.errors import *
from commands.command import Command
import GoogleAPI
import RiotAPI


DATA_FOLDER = 'data/'
CONFIG_FILE = 'config.ini'
SUGGESTION_FILE = DATA_FOLDER + 'suggestions.txt'
DATABASE_FILE = DATA_FOLDER + 'database.json'
REMINDERS_FILE = DATA_FOLDER + 'reminders.json'


client = discord.Client()


class LinkBot:
    def __init__(self):
        # If the config file doesn't exist, create it with the defaults.
        if not os.path.isfile(CONFIG_FILE):
            create_config(CONFIG_FILE)
            raise InitializationError("Config has been created. Fill out the required information before continuing.")

        self.restart = False
        self.paused = False

        self.lolgame_region = 'na'
        self.commands = {}
        self.events = {}
        self.data = load_json(DATABASE_FILE)
        # { serverID: {
        #       "admins" : [ userID, ... ],
        #       "birthdays" : { name : birthday, ...},
        #       "quotes" : [ ( text, author ), ... ]
        # }

        # All server ids are stored as strings by the json module.
        # Thus, they must get converted into integers here before they can be used with discord.py.
        records = [(key, val) for (key, val) in self.data.items()]
        for (key, val) in records:
            self.data[int(key)] = val
            del self.data[key]

        options = IniIO(CONFIG_FILE)
        self.owner_id = options.get_int('ownerDiscordId', default=None)
        self.owner = None
        self.token = options.get_str('botToken', default=None)
        self.client_id = options.get_int('botClientId', default=None)
        self.client_secret = options.get_str('botClientSecret', default=None)
        self.prefix = options.get_str('prefix', default=None)
        google_apikey = options.get_str('googleApiKey', default=None)
        self.googleClient = GoogleAPI.Client(google_apikey) if google_apikey is not None else None
        riot_apikey = options.get_str('riotApiKey', default=None)
        self.riotClient = RiotAPI.Client(riot_apikey) if riot_apikey is not None else None
        self.debug = options.get_bool('debug')

        if self.token is None or self.client_id is None or self.client_secret is None:
            raise InitializationError("'botToken', 'botClientId', and 'botClientSecret' must be specified in {}."
                                      .format(CONFIG_FILE))
        if self.owner_id is None:
            raise InitializationError("'ownerDiscordId' must be specified with your Discord user ID in {}."
                                      .format(CONFIG_FILE))
        if self.prefix is None:
            raise InitializationError("'prefix' must be specified in {} for proper functionality."
                                      .format(CONFIG_FILE))


    def run(self):
        logging.info('Initializing and logging in...')
        client.run(self.token)
        logging.info('Bot has been logged out.')
        if self.restart:
            logging.info("Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)


bot = LinkBot()


def event(func):
    e = func.__name__[3:]
    @client.event
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)
        if e in bot.events.keys():
            for f in bot.events[e]:
                await f(*args, **kwargs)
    bot.events[e] = []
    return wrapper


@event
async def on_ready():

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Print out various information about the bot for this session.
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    bot.owner = client.get_user(bot.owner_id)
    if bot.owner is None:
        raise InitializationError("Bot owner could not be found in any servers that the bot is a part of.")
    logging.info('Prefix: ' + "'" + bot.prefix + "'")
    if bot.debug:
        await client.change_presence(activity=discord.Game('DEVELOPMENT'))
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await client.change_presence(activity=discord.Game('{}help'.format(bot.prefix)))
    logging.info('LinkBot is ready.')


@event
async def on_member_join(member):
    pass


@event
async def on_message(message):
    if message.author.id != client.user.id:
        logging.info("Received a message from " + message.author.name)
        cmd = Command(bot, message)

        # if the message has the prefix or the channel is a DM, then the message is targeted at the bot.
        if cmd.has_prefix or cmd.is_dm:
            if not bot.paused or (bot.paused and cmd.command_arg.lower() == 'unpause'):
                if cmd.is_valid:
                    await cmd.run()
                else:
                    message.channel.send('"{}" is not a valid command.'.format(cmd.command_arg))


@client.event
async def on_error(event_name, *args, **kwargs):
    etype, e, tb = sys.exc_info()
    ch = e.cmd.channel
    if etype is InitializationError:
        raise e
    elif etype is CommandSyntaxError:
        subcmd = e.cmd.message.content[:e.cmd.message.content.find(e.cmd.argstr)].strip()
        await ch.send("{} {} Try `{}help {}` for help on how to use `{}`."
                      .format('WARN |', e, bot.prefix, e.cmd.command_arg, subcmd))
    elif etype is CommandPermissionError:
        await ch.send("{} {}".format('NOENTRY |', e))
    elif etype is DeveloperError:
        fmt_exc = traceback.format_exception(etype, e, tb)
        await ch.send("{} {}".format('EXCLAIM |', e.public_reason))
        await bot.owner.send("A DeveloperError has occurred:\n{}\n```{}```".format(e, fmt_exc))
    elif etype is CommandError:
        await ch.send("{} {}".format('X |', e))
    elif etype is LinkBotError:
        fmt_exc = traceback.format_exception(etype, e, tb)
        await bot.owner.send("A generic LinkBot has occurred:\n{}\n```{}```".format(e, fmt_exc))
    elif etype is EventError:
        fmt_exc = traceback.format_exception(etype, e, tb)
        await bot.owner.send("A generic EventError has occurred:\n  In event `{}`: {}\n```{}```"
                             .format(event_name, e, fmt_exc))
    else:
        fmt_exc = traceback.format_exception(etype, e, tb)
        await bot.owner.send("A {} has occurred:\n```{}```".format(etype, fmt_exc))



cmd_dir = 'commands/modules/'
for file in [cmd_dir + f for f in os.listdir(cmd_dir)]:
    if not file.endswith('__init__.py'):
        package = file.replace('/', '.')[:-3]
        _ = import_module(package)
