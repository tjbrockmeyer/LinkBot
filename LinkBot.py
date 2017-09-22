import threading
import time
import discord
import asyncio
import logging
from typing import Union

import Commands
from FileWriting import load_config, load_admins, load_quotes
from Helper import link_bot, client, google_api

from Sensitive import DISCORD_API_KEY, PAULS_SERVER_ID, ENTRY_LEVEL_ROLE_ID

DEBUG = False
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] [%(threadName)-10s] %(message)s')


def main():
    logging.info('Initializing and logging in...')
    botThread = threading.Thread(name='DiscordBot', target=thread_discord_bot)
    botThread.start()

    messageSender = threading.Thread(name='MSG_Send', target=thread_send_message, args=(asyncio.get_event_loop(),))
    messageSender.setDaemon(True)
    messageSender.start()

    # wait for the bot to become active.
    while not link_bot.active:
        logging.info('Waiting for bot to start.')
        time.sleep(1)

    # while the bot is active, we can do and process other things here.
    while not link_bot.isStopping:
        # dothingshere.....
        # ...
        # ...
        time.sleep(1)

    logging.info('Waiting on message sender thread.')
    messageSender.join()
    logging.info('Logging bot out.')
    asyncio.run_coroutine_threadsafe(client.logout(), asyncio.get_event_loop())
    botThread.join()
    logging.info('Bot has been logged out. Closing gracefully.')


# adds a message that is to be sent to the message queue. The message is then sent by the send message thread.
def SendMessage(destination: Union[discord.Channel, discord.Member, discord.User], message: str):
    link_bot.messages_to_send.put((destination, message))


# sends a message the the owner containing details on some error. Does nothing if there is no owner.
def SendErrorMessage(message: str):
    if link_bot.owner is not None:
        SendMessage(link_bot.owner, message)
    logging.error(message)


# starts the discord bot on a separate thread.
def thread_discord_bot():
    while not link_bot.requestedStop:
        try:
            logging.info("Bot thread started.")
            asyncio.set_event_loop(asyncio.new_event_loop())
            client.run(DISCORD_API_KEY)
            logging.info("Bot thread closing.")
        except Exception as e:
            logging.info("An Exception occurred. {0}".format(e))

            if not link_bot.encounteredError:
                link_bot.encounteredError = True
                link_bot.error = e


# the thread that sends messages
def thread_send_message(loop):
    logging.info("Send Message thread started.")
    while not link_bot.messages_to_send.empty() or not link_bot.isStopping or link_bot.active:
        packet = link_bot.messages_to_send.get()
        logging.info('Sending message to {0}: {1}.'.format(packet[0], packet[1]))
        asyncio.run_coroutine_threadsafe(client.send_message(packet[0], ("`[DEBUG]` " + packet[1] if DEBUG else packet[1])), loop)
    time.sleep(1)  # wait for any final commands to send.


# runs commandFunc on a new thread, passing it message and argstr. name becomes the name of the thread.
def run_command(commandFunc, message, argstr, name):
    commandThread = threading.Thread(name='cmd_' + name, target=commandFunc, args=(message, argstr, asyncio.get_event_loop()))
    commandThread.start()


# some initialization and setting members with no role to the entry level role [Paul's server only]
@client.event
async def on_ready():
    # read various files and set their values in the program.
    with link_bot.lock:
        load_config()
        load_admins()
        load_quotes()

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

    # set google api safe search settings from config
    google_api.set_safe_search(link_bot.nsfw)

    if DEBUG:
        await client.change_presence(game=discord.Game(name="Getting worked on"))
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await client.change_presence(game=discord.Game(name="{0}help".format(link_bot.prefix)))

    logging.info('Logged in as {0} with ID: {1}'.format(client.user.name, client.user.id))
    if link_bot.owner is not None:
        logging.info('Owner is {0}'.format(link_bot.owner.name))
    else:
        logging.info('Owner is not specified.')
    logging.info('Prefix: ' + "'" + link_bot.prefix + "'")
    logging.info('Active on these servers: ({0})'.format(len(client.servers)))
    for server in client.servers:
        logging.info('\t{0}'.format(server.name))

    # IN MEN OF THE NORTH, SET ALL NO-ROLE PEOPLE TO ENTRY-LEVEL ROLE
    for server in client.servers:
        if server.id == PAULS_SERVER_ID:
            entry_level_role = discord.utils.get(server.roles, id=ENTRY_LEVEL_ROLE_ID)
            for member in server.members:
                if len(member.roles) == 1:
                    await client.add_roles(member, entry_level_role)

    link_bot.active = True
    logging.info('Bot is ready.')

    # if an error occurred previously that caused the bot to restart, write a message about it.
    if link_bot.encounteredError:
        SendErrorMessage("An error occurred, causing a restart. "
                           "Other errors may have followed, but this is the original: \n{0}".format(link_bot.error))
        link_bot.encounteredError = False
        link_bot.error = None


# sets new members' role to the entry level role [Paul's server only]
@client.event
async def on_member_join(member: discord.Member):
    # ON MEMBER JOIN "MEN OF THE NORTH"
    if member.server.id is PAULS_SERVER_ID:  # check for 'is paul's server'
        role = discord.utils.get(member.server.roles, id=ENTRY_LEVEL_ROLE_ID)  # find entry level role
        await client.add_roles(member, role)  # assign it


# gets a message, splits it into (command, argstr), then starts the command on a new thread.
@client.event
async def on_message(message: discord.Message):
    if not link_bot.isStopping and message.author.id != client.user.id:
        logging.info("Received a message from " + message.author.name)

        # Set to lowercase and check for -> remove the prefix.
        original_content = str(message.content)
        has_prefix = False
        if original_content.startswith(link_bot.prefix):
            original_content = original_content[len(link_bot.prefix):]
            has_prefix = True

        # if the message has the prefix or the channel is private, then the message is targeted at the bot.
        if has_prefix or (message.channel.is_private and message.author.id != client.user.id):
            logging.info("The message was to me! It's from {0} in {1}: {2}".format(message.author, message.channel, message.content))
            altered_content = original_content.lower()
            try:
                command = altered_content[:altered_content.index(' ')]
            except ValueError:
                command = altered_content

            argstr = altered_content[len(command):].strip()

            if command == 'help':
                run_command(Commands.help, message, argstr, 'help')
            elif command == 'migrate':
                run_command(Commands.migrate, message, argstr, 'migrate')
            elif command == 'quote':
                run_command(Commands.quote, message, argstr, 'quote')
            elif command == 'birthday':
                run_command(Commands.birthday, message, argstr, 'birthday')
            elif command == 'lolgame':
                run_command(Commands.lolgame, message, argstr, 'lolgame')
            elif command == 'yt' or command == 'youtube':
                run_command(Commands.youtube, message, argstr, 'youtube')
            elif command == 'img' or command == 'image':
                run_command(Commands.image, message, argstr, 'image')
            elif command == 'play':
                run_command(Commands.play, message, argstr, 'play')
            elif command == 'suggest':
                run_command(Commands.suggest, message, argstr, 'suggest')
            elif command == 'nsfw':
                run_command(Commands.nsfw, message, argstr, 'nsfw')
            elif command == 'admin':
                run_command(Commands.admin, message, argstr, 'admin')
            elif command == 'logout' or command == 'logoff':
                run_command(Commands.logout, message, argstr, 'logout')
            else:
                SendMessage(message.channel, '"' + command + '" is not a valid command.')


if __name__ == "__main__":
    main()

