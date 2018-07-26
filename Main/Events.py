import logging
import discord
from Main.LinkBot import bot, LinkBotError
from Commands.Command import Command


MY_SERVER_ID = 153368514390917120
ENTRY_LEVEL_ROLE_ID = 215608168519172096


# some initialization and setting members with no role to the entry level role [Paul's server only]
@bot.discordClient.event
async def on_ready():

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Print out various information about the bot for this session.
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    logging.info('Logged in as {0} with ID: {1}'
                 .format(bot.discordClient.user.name, bot.discordClient.user.id))
    logging.info('Active on these servers: ({0})'.format(len(bot.discordClient.guilds)))
    for server in bot.discordClient.guilds:
        logging.info('\t{0}'.format(server.name))

    logging.info("Owner: {}:{}".format(type(bot.owner), bot.owner))
    bot.owner = bot.discordClient.get_user(bot.owner_id)
    if bot.owner is None:
        raise LinkBotError("Bot owner could not be found in any servers that the bot is a part of.")
    logging.info('Prefix: ' + "'" + bot.prefix + "'")

    # CREATE SERVER-SIDE SESSION OBJECTS
    bot.build_session_objects()

    if bot.debug:
        await bot.set_game("Debug")
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await bot.set_game("{}.help".format(bot.prefix))

    # IN MY_SERVER, SET ALL NO-ROLE PEOPLE TO ENTRY-LEVEL ROLE.
    for server in bot.discordClient.guilds:
        if server.id == MY_SERVER_ID:
            entry_level_role = discord.utils.get(server.roles, id=ENTRY_LEVEL_ROLE_ID)
            for member in server.members:
                if len(member.roles) == 1:
                    await bot.discordClient.add_roles(member, entry_level_role)

    # CHECK FOR SOMEONE'S BIRTHDAY BEING TODAY, IF SO, SEND A MESSAGE TO EVERYONE.
    if not bot.debug:
        from Commands.Funcs.Birthday import birthday_check
        birthday_check()

    bot.active = True
    logging.info('Bot is ready.')


# sets new members' role to the entry level role [Paul's server only]
@bot.discordClient.event
async def on_member_join(member):
    # ON MEMBER JOIN "MEN OF THE NORTH"
    if member.server.id is MY_SERVER_ID:  # check for 'is paul's server'
        role = discord.utils.get(member.server.roles, id=ENTRY_LEVEL_ROLE_ID)  # find entry level role
        await bot.discordClient.add_roles(member, role)  # assign it


# gets a message, splits it into (command, argstr), then starts the command on a new thread.
@bot.discordClient.event
async def on_message(message):
    if bot.isReadingCommands and message.author.id != bot.discordClient.user.id:
        logging.info("Received a message from " + message.author.name)

        cmd = Command(message)

        # if the message has the prefix or the channel is a DM, then the message is targeted at the bot.
        if cmd.has_prefix or cmd.is_dm:
            if not bot.paused or (bot.paused and cmd.command.lower() == 'unpause'):
                if cmd.is_valid:
                    bot.run_command(cmd)
                else:
                    bot.send_message(message.channel, '"' + cmd.command + '" is not a valid command.')