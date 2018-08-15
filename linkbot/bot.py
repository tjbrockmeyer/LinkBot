import logging
import os
import sys
import discord
import traceback
from functools import wraps, reduce
from importlib import import_module

import GoogleAPI
import RiotAPI
import linkbot.utils.database as db
from linkbot.errors import *
from linkbot.utils.ini import Ini
from linkbot.utils import emoji
from linkbot.utils.command import Command
from linkbot.utils.misc import create_config, split_message


class LinkBot:
    def __init__(self):
        # If the config file doesn't exist, create it with the defaults.
        if not os.path.isfile(config_ini):
            create_config(config_ini)
            raise InitializationError("Config has been created. Fill out the required information before continuing.")

        self.restart = False
        self.commands = {}
        self.events = {}

        options = Ini.load(config_ini)
        self.owner_id = options.get_int('ownerDiscordId')
        self.owner = None
        self.token = options.get_str('bot.token')
        self.client_id = options.get_int('bot.clientId')
        self.client_secret = options.get_str('bot.clientSecret')
        self.prefix = options.get_str('prefix')
        self.debug = options.get_bool('debug')

        google_apikey = options.get_str('apikeys.google')
        self.googleClient = GoogleAPI.Client(google_apikey) if google_apikey else None
        riot_apikey = options.get_str('apikeys.riotgames', default=None)
        self.riotClient = RiotAPI.Client(riot_apikey) if riot_apikey is not None else None

        if not self.token or not self.client_id or not self.client_secret:
            raise InitializationError(
                f"'token', 'clientId', and 'clientSecret' must be specified in {config_ini}.")
        if not self.owner_id:
            raise InitializationError(
                f"'ownerDiscordId' must be specified with your Discord user ID in {config_ini}.")
        if not self.prefix:
            raise InitializationError(f"'prefix' must be specified in {config_ini} for proper functionality.")

    def run(self):
        if bot.debug:
            client.run(self.token)
            return

        from pathlib import Path
        if os.path.isfile('INSTANCE'):
            raise InitializationError("Only one instance may be running at a time.")
        Path('INSTANCE').touch()
        logging.info('Initializing and logging in...')
        try:
            client.run(self.token)
        finally:
            os.remove('INSTANCE')

        logging.info('Bot has been logged out.')
        if self.restart:
            logging.info("Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)

    @staticmethod
    def embed(c: discord.Color, ft: str="", **kwargs):
        return discord.Embed(color=c, **kwargs) \
            .set_footer(text=ft if ft else client.user.display_name, icon_url=client.user.avatar_url)


cmd_dir = 'linkbot/commands/'
config_ini = 'config.ini'
client = discord.Client()
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
    bot.owner = client.get_user(bot.owner_id)
    if bot.owner is None:
        raise InitializationError("Bot owner could not be found in any servers that the bot is a part of.")
    logging.info('Prefix: ' + "'" + bot.prefix + "'")
    if bot.debug:
        await client.change_presence(activity=discord.Game(name='Development'))
        logging.info('Currently running in DEBUG mode. Edit source with DEBUG = False to deactivate.')
    else:
        await client.change_presence(activity=discord.Game(name=f'{bot.prefix}help'))
    logging.info('LinkBot is ready.')


@event
async def on_member_join(member):
    pass


@event
async def on_guild_join(guild):
    # Add an entry for this guild into the database.
    with db.connect() as (conn, cur):
        cur.execute(
            """
            INSERT INTO servers (server_id)
            VALUES (%s);
            """, [guild.id])
        conn.commit()


@event
async def on_guild_remove(guild):
    with db.connect() as (conn, cur):
        cur.execute("DELETE FROM servers WHERE server_id = %s CASCADE;", [guild.id])
        conn.commit()


@event
async def on_message(message):
    if not message.author.bot:
        logging.info("Received a message from " + message.author.name)
        cmd = Command(bot, message)

        # if the message has the prefix or the channel is a DM, then the message is targeted at the bot.
        if cmd.has_prefix or cmd.is_dm:
            if cmd.is_valid:
                await cmd.run()
            else:
                raise CommandError(cmd, f'"{cmd.command_arg}" is not a valid command.')


@client.event
async def on_error(event_name: str, *args, **kwargs):
    etype, e, tb = sys.exc_info()
    fmt_exc = reduce(lambda x, y: f"{x}{y}", traceback.format_exception(etype, e, tb), "")
    if etype is InitializationError:
        raise e
    if issubclass(etype, CommandError):
        ch = e.cmd.channel

        if etype is CommandSyntaxError:
            import linkbot.utils.menu as menu
            from linkbot.commands.Help import send_help

            async def req_help(_r, _u):
                await send_help(ch, e.cmd.command_arg)
            m = menu.Menu(
                embed=bot.embed(
                    discord.Color.red(),
                    title=f"{emoji.Symbol.warning} Syntax Error {emoji.Symbol.warning}",
                    description=f"{e}\n\n"
                                f"For more help, Try `{bot.prefix}help {e.cmd.command_arg}`,\n"
                                f"or react with {emoji.Symbol.grey_question}"),
                show_navigation=False)\
                .set_options([menu.Option(emoji.Symbol.grey_question, "", func=req_help, close=True)])
            await menu.send(ch, m, timeout=30, destroy_on_close=False, only_accept=e.cmd.author)

        elif etype is CommandPermissionError:
            await ch.send(embed=bot.embed(
                discord.Color.red(),
                title=f"{emoji.Symbol.no_entry} Permission Error {emoji.Symbol.no_entry}",
                description=str(e)))

        elif etype is DeveloperError:
            await ch.send(embed=bot.embed(
                discord.Color.red(),
                title=f"{emoji.Symbol.exclamation} Unknown Error {emoji.Symbol.exclamation}",
                description=e.public_reason + "\nAn error report was automatically sent."))
            await _send_traceback(fmt_exc)

        elif etype is CommandError:
            await ch.send(embed=bot.embed(
                discord.Color.red(),
                title=f"{emoji.Symbol.x} Error {emoji.Symbol.x}",
                description=str(e)))
    else:
        await _send_traceback(fmt_exc)


async def _send_traceback(tb):
    logging.error(tb)
    for msg in split_message(tb, 1994):
        await bot.owner.send(f"```{msg}```")


# Database setup and test.
if not db.setup(config_ini):
    raise InitializationError(
        f"Failed to connect to the database. Be sure that your database settings in {config_ini} are properly set up.")
try:
    with db.connect():
        pass
except:
    raise InitializationError("Failed to connect to the database. Is the hostname correct, and is the database online?")

# Import all commands.
for file in [cmd_dir + f for f in os.listdir(cmd_dir)]:
    if os.path.isfile(file) and not file.endswith('__init__.py'):
        package = file.replace('/', '.')[:-3]
        _ = import_module(package)
