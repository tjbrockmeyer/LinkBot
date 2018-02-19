import logging
from datetime import datetime

import discord
from Commands.Command import Command

from Main.Bot import link_bot
from Main.FileWriting import load_config, load_data
from Main.Helper import SendMessage, SendErrorMessage, RunCommand
from Sensitive import MY_SERVER_ID, ENTRY_LEVEL_ROLE_ID


# some initialization and setting members with no role to the entry level role [Paul's server only]
@link_bot.discordClient.event
async def on_ready():
    # read various files and set their values in the program.
    with link_bot.lock:
        load_config()
        load_data()

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Print out various information about the bot for this session.
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    if link_bot.debug:
        await link_bot.discordClient.change_presence(game=discord.Game(name="Getting worked on"))
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await link_bot.discordClient.change_presence(game=discord.Game(name="{0}help".format(link_bot.prefix)))

    logging.info('Logged in as {0} with ID: {1}'
                 .format(link_bot.discordClient.user.name, link_bot.discordClient.user.id))

    if link_bot.owner is not None:
        logging.info('Owner is {0}'.format(link_bot.owner.name))
    else:
        logging.info('Owner is not specified.')

    logging.info('Prefix: ' + "'" + link_bot.prefix + "'")

    logging.info('Active on these servers: ({0})'.format(len(link_bot.discordClient.servers)))
    for server in link_bot.discordClient.servers:
        logging.info('\t{0}'.format(server.name))

    # Report errors that have occurred.
    if link_bot.error is not None:
        SendErrorMessage(link_bot.error)
        SendErrorMessage(link_bot.error.with_traceback())
        link_bot.error = None

    # CREATE SERVER-SIDE SESSION OBJECTS
    link_bot.BuildSessionObjects()

    # IN MY_SERVER, SET ALL NO-ROLE PEOPLE TO ENTRY-LEVEL ROLE.
    for server in link_bot.discordClient.servers:
        if server.id == MY_SERVER_ID:
            entry_level_role = discord.utils.get(server.roles, id=ENTRY_LEVEL_ROLE_ID)
            for member in server.members:
                if len(member.roles) == 1:
                    await link_bot.discordClient.add_roles(member, entry_level_role)

    # CHECK FOR SOMEONE'S BIRTHDAY BEING TODAY, IF SO, SEND A MESSAGE TO EVERYONE.
    if not link_bot.debug:
        today = datetime.now()
        for server in link_bot.discordClient.servers:
            if server.id in link_bot.data and 'birthdays' in link_bot.data[server.id]:
                for p, b in link_bot.data[server.id]['birthdays'].items():
                    bday = datetime.strptime(b, "%m/%d")
                    if bday.day == today.day and bday.month == today.month:
                        await link_bot.discordClient.send_message(
                            discord.utils.get(server.channels, is_default=True),
                            "@everyone Today is {0}'s birthday!".format(p))


    link_bot.active = True
    logging.info('Bot is ready.')


# sets new members' role to the entry level role [Paul's server only]
@link_bot.discordClient.event
async def on_member_join(member):
    # ON MEMBER JOIN "MEN OF THE NORTH"
    if member.server.id is MY_SERVER_ID:  # check for 'is paul's server'
        role = discord.utils.get(member.server.roles, id=ENTRY_LEVEL_ROLE_ID)  # find entry level role
        await link_bot.discordClient.add_roles(member, role)  # assign it


# gets a message, splits it into (command, argstr), then starts the command on a new thread.
@link_bot.discordClient.event
async def on_message(message):
    if link_bot.isReadingCommands and message.author.id != link_bot.discordClient.user.id:
        logging.info("Received a message from " + message.author.name)

        cmd = Command(message)

        # if the message has the prefix or the channel is private, then the message is targeted at the bot.
        if cmd.hasPrefix or cmd.channel.is_private:
            if not link_bot.paused or (link_bot.paused and cmd.command.lower() == 'unpause'):
                if cmd.isValid:
                    RunCommand(cmd)
                else:
                    SendMessage(message.channel, '"' + cmd.command + '" is not a valid command.')