import logging
from datetime import datetime

import discord

from Helper import SendMessage, SendErrorMessage, RunCommand
from Sensitive import PAULS_SERVER_ID, ENTRY_LEVEL_ROLE_ID
from Bot import link_bot


# some initialization and setting members with no role to the entry level role [Paul's server only]
@link_bot.discordClient.event
async def on_ready():
    from FileWriting import load_config, load_admins, load_quotes, load_birthdays

    # read various files and set their values in the program.
    with link_bot.lock:
        load_config()
        load_admins()
        load_quotes()
        load_birthdays()

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

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

    # IN MEN OF THE NORTH, SET ALL NO-ROLE PEOPLE TO ENTRY-LEVEL ROLE
    for server in link_bot.discordClient.servers:
        if server.id == PAULS_SERVER_ID:
            entry_level_role = discord.utils.get(server.roles, id=ENTRY_LEVEL_ROLE_ID)
            for member in server.members:
                if len(member.roles) == 1:
                    await link_bot.discordClient.add_roles(member, entry_level_role)

    if not link_bot.debug:
        today = datetime.now()
        for server in link_bot.discordClient.servers:
            if server.id in link_bot.birthdays:
                for p, b in link_bot.birthdays[server.id].items():
                    if b.day == today.day and b.month == today.month:
                        await link_bot.discordClient.send_message(
                            discord.utils.get(server.channels, is_default=True),
                            "@everyone Today is {0}'s birthday! Happy Birthday {0}!".format(p)
                        )


    link_bot.active = True
    logging.info('Bot is ready.')

    # if an error occurred previously that caused the bot to restart, write a message about it.
    if link_bot.encounteredError:
        SendErrorMessage("An error occurred, causing a restart. "
                           "Other errors may have followed, but this is the original: \n{0}".format(link_bot.error))
        link_bot.encounteredError = False
        link_bot.error = None


# sets new members' role to the entry level role [Paul's server only]
@link_bot.discordClient.event
async def on_member_join(member):
    # ON MEMBER JOIN "MEN OF THE NORTH"
    if member.server.id is PAULS_SERVER_ID:  # check for 'is paul's server'
        role = discord.utils.get(member.server.roles, id=ENTRY_LEVEL_ROLE_ID)  # find entry level role
        await link_bot.discordClient.add_roles(member, role)  # assign it


# gets a message, splits it into (command, argstr), then starts the command on a new thread.
@link_bot.discordClient.event
async def on_message(message):
    from Command import Command
    if not link_bot.isStopping and message.author.id != link_bot.discordClient.user.id:
        logging.info("Received a message from " + message.author.name)

        cmd = Command(message)

        # if the message has the prefix or the channel is private, then the message is targeted at the bot.
        if cmd.hasPrefix or cmd.channel.is_private:
            if cmd.isValid:
                RunCommand(cmd)
            else:
                SendMessage(message.channel, '"' + cmd.command + '" is not a valid command.')