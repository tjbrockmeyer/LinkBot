import threading
import traceback
import logging
import asyncio
import time
import os
import sys
from queue import Queue
from Main.Funcs import read_config, load_json, save_json

import discord
import GoogleAPI
import RiotAPI


DATA_FOLDER = 'data/'
CONFIG_FILE = DATA_FOLDER + 'config.txt'
SUGGESTION_FILE = DATA_FOLDER + 'suggestions.txt'
DATABASE_FILE = DATA_FOLDER + 'database.json'


class LinkBotError(Exception):
    pass


class SessionObject:
    def __init__(self):
        self.original_deck = []
        self.deck = []


class LinkBot:
    def __init__(self):
        self.active = False
        self.isReadingCommands = True
        self.restart = False
        self.paused = False

        self.client = discord.Client()
        self.messages_to_send = Queue()
        self.messages_received = Queue()
        self.lock = threading.RLock()

        self.lolgame_region = 'na'
        self.session_objects = {}
        self.data = load_json(DATABASE_FILE)
        # { serverID: {
        #       "admins" : [ userID, ... ],
        #       "birthdays" : { name : birthday, ...},
        #       "quotes" : [ ( text, author ), ... ]
        # }

        # Read from the config file
        if not os.path.isfile(CONFIG_FILE):  # if the config file doesn't exist, create it with the defaults.
            self.create_config()
            raise LinkBotError("Config has been created. Fill out the required information before continuing.")

        options = read_config(CONFIG_FILE)
        self.owner_id = options.get('ownerDiscordId')
        self.token = options.get('botToken')
        self.client_id = options.get('botClientId')
        self.client_secret = options.get('botClientSecret')
        self.prefix = options.get('prefix')
        debug = options.get('debug')
        google_apikey = options.get('googleApiKey')
        riot_apikey = options.get('riotApiKey')

        if self.token is None or self.client_id is None or self.client_secret is None:
            raise LinkBotError("All three of 'botToken', 'botClientId', and 'botClientSecret' must be specified in {}.".format(CONFIG_FILE))
        if self.owner_id is None:
            raise LinkBotError("'ownerDiscordId' must be specified with your Discord user ID in {}.".format(CONFIG_FILE))
        if self.prefix is None:
            raise LinkBotError("'prefix' must be specified in {} for proper functionality.".format(CONFIG_FILE))

        self.owner_id = int(self.owner_id)
        self.owner = None
        self.client_id = int(self.client_id)
        self.debug = False if debug is None else (True if debug.lower() in ['t', 'true', '1'] else False)

        self.googleClient = GoogleAPI.Client(google_apikey) if google_apikey is not None else None
        self.riotClient = RiotAPI.Client(riot_apikey) if riot_apikey is not None else None

    # runs commandFunc on a new thread, passing it message and argstr. name becomes the name of the thread.
    def run_command(self, cmd):
        commandThread = threading.Thread(name='cmd_' + cmd.command, target=LinkBot._safe_command_func, args=(self, cmd))
        commandThread.start()

    # adds a message that is to be sent to the message queue. The message is then sent by the send message thread.
    def send_message(self, destination, message='', embed=None):
        if len(message) > 2000:
            split_index = message.rfind('\n', 0, 2000)
            if split_index == -1:
                split_index = 2000
            self.send_message(destination, message[:split_index], embed)
            self.send_message(destination, message[split_index:], embed)
        else:
            self.messages_to_send.put((destination, message, embed))

    # sends a message the the owner containing details on some error. Does nothing if there is no owner.
    def send_error_message(self, message: str):
        self.send_message(self.owner, message)
        logging.error(message)

    def on_syntax_error(self, command: str, info='', cmd_name=None) -> str:
        """
        To be called when there has been a syntax error in a command.
        Returns info and command formatted into a help string.

        :param command: The command that received a syntax error.
        :type command: str
        :param info: Some info as to what went wrong with the syntax.
        :type info: str
        :param cmd_name: Alternative name for the command - usually for a sub-command.
        :type cmd_name: str
        :return: A new string with the parameters formatted in.
        :rtype: str
        """
        return "{info} Try `{prefix}help {cmd}` for help on how to use `{cmd_name}." \
            .format(prefix=self.prefix, cmd=command, info=info, cmd_name=(command if cmd_name is None else cmd_name)) \
            .lstrip()

    def is_admin(self, member):
        """
        Checks if the member is an admin.

        :param discord.Member member: Member to check if they're an admin.
        :return: True if the member is an admin, False otherwise.
        :rtype: bool
        """
        if self.is_owner(member):
            return True
        if member.server.id not in self.data:
            return False
        if 'admins' not in self.data[member.server.id]:
            return False
        return member.id in self.data[member.server.id]['admins']

    def is_owner(self, user):
        """
        Checks if the user is the bot's owner.

        :param discord.User user:
        :return: True if the user is the bot's owner, False otherwise.
        :rtype: bool
        """
        return user.id == self.owner.id

    async def set_game(self, title):
        await self.client.change_presence(activity=discord.Game(name=title))

    def build_session_objects(self):
        for server in self.client.guilds:
            self.session_objects[server] = SessionObject()

    def save_data(self):
        with self.lock:
            save_json(DATABASE_FILE, self.data)
        logging.info("Database saved.")

    # create a default config file with documentation.
    def create_config(self):
        with self.lock:
            if not os.path.isdir('data'):
                os.mkdir('data')
            with open(CONFIG_FILE, 'w') as cfg:
                cfg.writelines([
                    '# Server owner discord id\n',
                    '# Set this to your own id in order to use owner commands\n',
                    '# Owner is automatically an admin and is allowed to use admin commands as well.\n',
                    '# You need to know your data-side id for this, so turn on dev options in your\n'
                    '# user settings on discord, then right click yourself and copy your ID.\n',
                    'ownerDiscordId=\n\n',

                    "# Information regarding the bot.\n",
                    "# These are all found on your discord developer page: https://discordapp.com/developers/applications\n",
                    "# Select your bot, and under 'General Information', botClientId and botClientSecret and be found.\n",
                    "# Under the 'Bot' tab, botToken can be found.\n",
                    "botToken=\n",
                    "botClientId=\n",
                    "botClientSecret=\n\n",

                    "# Key for accessing Riot Games' API.\n",
                    "riotApiKey=\n",
                    "# Key for accessing Google's API (Image search and YouTube search).\n",
                    "googleApiKey=\n\n",

                    "# Prefix for using commands with this bot.\n",
                    "# Preceed any command being issued to the bot with this prefix.\n",
                    "# Commands being sent of a DM to the bot do not require this prefix.\n",
                    "# Default (with no quotes): \"link.\"\n"
                    "prefix=link.\n\n",

                    "debug=False\n",
                ])
        logging.info('Created config file.')

    # ########################### #
    # RUNNING THE BOT AND THREADS #
    # ########################### #

    # Runs the bot in a multithreaded mode.
    def run_threaded(self):
        logging.info('Initializing and logging in...')

        messageSender = threading.Thread(
            name='MSG_Send', target=self._send_message_thread, args=(asyncio.get_event_loop(),))
        messageSender.setDaemon(True)
        messageSender.start()

        self.client.run(self.token)
        logging.info('Bot has been logged out.')

        if self.restart:
            logging.info("Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)

    @staticmethod
    def _safe_command_func(b, cmd):
        try:
            asyncio.set_event_loop(cmd.loop)
            asyncio.run_coroutine_threadsafe(cmd.info.func(cmd), cmd.loop)
        except:
            from functools import reduce
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = reduce(lambda x, y: "{}{}".format(x, y), traceback.format_exception(exc_type, exc_value, exc_traceback), "")
            b.send_error_message("Exception occurred in `cmd_{}(cmd)`: ```{}```".format(cmd.info.command, tb))


    # the thread that sends messages
    def _send_message_thread(self, loop):
        logging.info("Send Message thread started.")

        # This is a blocking call. Waits for messages to enter the message queue.
        # While there are messages, or we are still reading, or the bot is still active...
        while not self.messages_to_send.empty() or self.active or self.isReadingCommands:
            channel, message, embed = self.messages_to_send.get()
            logging.info('Sending message ' +
                         ('with embed ' if embed is not None else '') +
                         'to {}: {}'.format(channel, message))

            # Check if the message has an embed. If so, apply it.
            if embed is None:
                asyncio.run_coroutine_threadsafe(channel.send(
                    ("`[DEBUG]` " + message if self.debug else message)), loop)
            else:
                asyncio.run_coroutine_threadsafe(channel.send(
                    ("`[DEBUG]` " + message if self.debug else message), embed=embed), loop)
        time.sleep(1)  # wait for any final commands to send.


bot = LinkBot()
