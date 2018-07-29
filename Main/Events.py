import logging
import asyncio
from Main.LinkBot import bot, LinkBotError
from Commands.Command import Command
from functools import wraps


def call_events(func):
    event = func.__name__[3:]
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await func(*args, **kwargs)
        if event in bot.events.keys():
            for f in bot.events[event]:
                await f(*args, **kwargs)
    bot.events[event] = []
    return wrapper


@bot.client.event
@call_events
async def on_ready():

    # load voice module
    # discord.opus.load_opus('opus')
    # if not discord.opus.is_loaded():
    #    await logging.info('WARNING:\tOpus failed to load. Voice is disabled for this session.')

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Print out various information about the bot for this session.
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    logging.info('Logged in as {} with ID: {}'
                 .format(bot.client.user.name, bot.client.user.id))
    logging.info('Active on these servers: ({})'.format(len(bot.client.guilds)))
    for server in bot.client.guilds:
        logging.info('\t{}'.format(server.name))
    bot.owner = bot.client.get_user(bot.owner_id)
    if bot.owner is None:
        raise LinkBotError("Bot owner could not be found in any servers that the bot is a part of.")
    logging.info('Prefix: ' + "'" + bot.prefix + "'")
    if bot.debug:
        await bot.set_game("Debug")
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await bot.set_game("{}help".format(bot.prefix))
    logging.info('Bot is ready.')


@bot.client.event
@call_events
async def on_member_join(member):
    pass


# gets a message, splits it into (command, argstr), then starts the command on a new thread.
@bot.client.event
async def on_message(message):
    if message.author.id != bot.client.user.id:
        logging.info("Received a message from " + message.author.name)
        cmd = Command(message)

        # if the message has the prefix or the channel is a DM, then the message is targeted at the bot.
        if cmd.has_prefix or cmd.is_dm:
            if not bot.paused or (bot.paused and cmd.command.lower() == 'unpause'):
                if cmd.is_valid:
                    future = asyncio.ensure_future(cmd.run())
                    result = await future
                else:
                    bot.send_message(message.channel, '"{}" is not a valid command.'.format(cmd.command))


# To register functions to be called by events.
import Commands.Funcs as _
