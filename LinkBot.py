import threading
import logging
import asyncio
import time
from queue import Queue

import discord

import GoogleAPI
import RiotAPI


class LinkBot:
    def __init__(self, google_api_key, riot_api_key):
        # setting this false along with isStopping will terminate the message sending thread.
        self.active = False
        # setting this to true will stop the retrieval of messages, and the program will wait for command threads to terminate.
        self.isStopping = False
        # if the bot is not active, but the stop was not requested, the bot will restart.
        self.requestedStop = False

        self.encounteredError = False
        self.error = None
        self.debug = False

        self.messages_to_send = Queue()
        self.messages_received = Queue()
        self.lock = threading.RLock()

        self.discordClient = discord.Client()
        self.googleClient = GoogleAPI.Client(google_api_key)
        self.riotClient = RiotAPI.Client(riot_api_key)

        # for each server, there is a list of user ids for registered admins.
        self.admins = dict()
        # for each server, there is a list of tuples containing (name, quote)
        self.quotes = dict()
        # for each server, there is a dictionary of names with a birthday.
        self.birthdays = dict()
        # for each server, there is a bool saying whether the nsfw filter is enabled on that server or not.
        self.nsfw = dict()

        # config settings
        self.owner = None
        self.prefix = 'link.'

        # other settings
        self.lolgame_region = 'na'


    def RunThreaded(self, discord_api_key):
        logging.info('Initializing and logging in...')

        botThread = threading.Thread(
            name='DiscordBot', target=self._thread_Bot, args=(discord_api_key,))
        botThread.start()

        messageSender = threading.Thread(
            name='MSG_Send', target=self._thread_SendMessage, args=(asyncio.get_event_loop(),))
        messageSender.setDaemon(True)
        messageSender.start()

        # wait for the bot to become active.
        while not self.active:
            logging.info('Waiting for bot to start.')
            time.sleep(1)

        # while the bot is active, we can do and process other things here.
        while not self.isStopping:
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


    def _thread_Bot(self, discord_api_key):
        logging.info("Bot thread started.")
        asyncio.set_event_loop(asyncio.new_event_loop())
        while not self.requestedStop:
            try:
                self.discordClient.run(discord_api_key)
            except Exception as e:
                logging.info("An Exception occurred. {0}".format(e))
                if not self.encounteredError:
                    self.encounteredError = True
                    self.error = e
        logging.info("Bot thread closing.")

    # the thread that sends messages
    def _thread_SendMessage(self, loop):
        logging.info("Send Message thread started.")
        while not self.messages_to_send.empty() or not self.isStopping or self.active:
            packet = self.messages_to_send.get()
            logging.info('Sending message to {0}: {1}.'.format(packet[0], packet[1]))
            asyncio.run_coroutine_threadsafe(self.discordClient.send_message(
                packet[0], ("`[DEBUG]` " + packet[1] if self.debug else packet[1])), loop)
        time.sleep(1)  # wait for any final commands to send.
