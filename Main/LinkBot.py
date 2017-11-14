import threading
import logging
import asyncio
import time
import os
import sys
from queue import Queue

import discord

import GoogleAPI
import RiotAPI


class ServerSideObject:
    def __init__(self):
        self.is_nsfw = False

        self.original_deck = []
        self.deck = []


class LinkBot:
    """
    :active: (bool = False) Setting this false along with isStopping will terminate the message sending thread.
    :paused: (bool = False)
    :debug: (bool = False)

    :messages_to_send: (Queue[(channel/user/member, str, Embed)])
    :messages_received: (Queue[Message])
    :lock: (threading.RLock)

    :discordClient: (discord.Client)
    :googleClient: (GoogleAPI.Client)
    :riotClient: (RiotAPI.Client)

    :data: (dict) server_id -> { admins, quotes, birthdays }. Permanently stored data.
    :server_object: (dict of ServerSideObject) Holds session-based server objects. Deleted upon bot logout.


    :owner: (User = None) Owner of the bot. Has access to owner-only commands and admin-only commands.
    :prefix: (str = "link.")
    """
    def __init__(self, google_api_key, riot_api_key):
        self.active = False
        self.isReadingCommands = True
        self.restart = False

        self.paused = False
        self.debug = False

        self.messages_to_send = Queue()
        self.messages_received = Queue()
        self.lock = threading.RLock()

        self.discordClient = discord.Client()
        self.googleClient = GoogleAPI.Client(google_api_key)
        self.riotClient = RiotAPI.Client(riot_api_key)

        self.data = {}
        # { serverID: {
        #       "admins" : [ userID, ... ],
        #       "birthdays" : { name : birthday, ...},
        #       "quotes" : [ ( quote, author ), ... ]
        # }
        self.server_object = {}

        # config settings
        self.owner = None
        self.prefix = 'link.'

        # other settings
        self.lolgame_region = 'na'

    def BuildSessionObjects(self):
        for server in self.discordClient.servers:
            self.server_object[server] = ServerSideObject()

    # Runs the bot in a multithreaded mode.
    def RunThreaded(self, discord_api_key):
        logging.info('Initializing and logging in...')

        # Create thread that runs the bot.
        botThread = threading.Thread(
            name='DiscordBot', target=self._thread_Bot, args=(discord_api_key,))
        botThread.start()

        # Create the thread that sends messages to channels and users.
        messageSender = threading.Thread(
            name='MSG_Send', target=self._thread_SendMessage, args=(asyncio.get_event_loop(),))
        messageSender.setDaemon(True)
        messageSender.start()

        # wait for the bot to become active. Bot becomes active through the BotThread, in the event on_ready.
        while not self.active:
            logging.info('Waiting for bot to start.')
            time.sleep(1)

        # while the bot is active, we can do and process other things here.
        # I was going to have a command line interface, but i haven't felt like getting it working.
        while self.isReadingCommands:
            # dothingshere.....
            # ...
            # ...
            time.sleep(1)

        logging.info('Waiting on message sender thread.')
        messageSender.join()
        logging.info('Logging bot out.')
        asyncio.run_coroutine_threadsafe(self.discordClient.logout(), asyncio.get_event_loop())
        botThread.join()
        logging.info('Bot has been logged out. Closing gracefully.')

        if self.restart:
            os.execl(sys.executable, sys.executable, *sys.argv)


    # Thread that runs main bot processes.
    def _thread_Bot(self, discord_api_key):
        logging.info("Bot thread started.")
        asyncio.set_event_loop(asyncio.new_event_loop())

        # Until a stop is requested, just keep restarting the bot if errors occur.
        # The try/except here might be useless.
        try:
            self.discordClient.run(discord_api_key)
        except Exception as e:
            logging.error("Bot thread crash through Exception: {0}".format(e))
        logging.info("Bot thread closing.")

    # the thread that sends messages
    def _thread_SendMessage(self, loop):
        logging.info("Send Message thread started.")

        # This is a blocking call. Waits for messages to enter the message queue.
        # While there are messages, or we are still reading, or the bot is still active...
        while not self.messages_to_send.empty() or self.active or self.isReadingCommands:
            packet = self.messages_to_send.get()
            logging.info('Sending message ' +
                         ('with embed ' if packet[2] is not None else '') +
                         'to {0}: {1}'.format(packet[0], packet[1]))

            # Check if the message has an embed. If so, apply it.
            if packet[2] is None:
                asyncio.run_coroutine_threadsafe(self.discordClient.send_message(
                    packet[0], ("`[DEBUG]` " + packet[1] if self.debug else packet[1])), loop)
            else:
                asyncio.run_coroutine_threadsafe(self.discordClient.send_message(
                    packet[0], ("`[DEBUG]` " + packet[1] if self.debug else packet[1]), embed=packet[2]), loop)
        time.sleep(1)  # wait for any final commands to send.
