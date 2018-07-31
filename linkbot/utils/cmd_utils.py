
import logging
import discord
from functools import wraps

from linkbot.bot import client
from linkbot.errors import *
from linkbot.utils.checks import *
from linkbot.utils.emoji import send_success
from linkbot.utils.command import Command, CommandInfo

DISABLE = 1
ADMIN_ONLY = 2
OWNER_ONLY = 4
SERVER_ONLY = 8
DM_ONLY = 16


def restrict(conditions, reason=''):
    def decorator(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            if DISABLE & conditions != 0:
                raise CommandPermissionError(
                    cmd, "`{}` is disabled. {}"
                         .format(_usrepl(func.__name__), "Reason: {}.".format(reason) if reason != '' else ''))
            elif OWNER_ONLY & conditions != 0 and not is_admin(cmd.author):
                raise CommandPermissionError(
                    cmd, "`{}` can only be used by the bot's owner: {}"
                         .format(_usrepl(func.__name__), bot.owner))
            elif ADMIN_ONLY & conditions != 0 and not is_admin(cmd.author):
                raise CommandPermissionError(
                    cmd, "`{}` can only be used by registered adnims. See `{}admin list`"
                         .format(_usrepl(func.__name__), bot.prefix))
            elif SERVER_ONLY & conditions != 0 and cmd.guild is None:
                raise CommandPermissionError(
                    cmd, "`{}` can only be used in a server."
                         .format(_usrepl(func.__name__)))
            elif DM_ONLY & conditions != 0 and not cmd.is_dm:
                raise CommandPermissionError(
                    cmd, "`{}` can only be used in a direct message."
                         .format(_usrepl(func.__name__)))
            else:
                await func(cmd, *args, **kwargs)
        return wrapper
    return decorator


def require_args(count):
    def decorator(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            if len(cmd.args) < count:
                raise CommandSyntaxError(
                    cmd, reason="At least {} argument{} necessary.".format(count, ' is' if count == 1 else 's are'))
            await func(cmd, *args, **kwargs)
        return wrapper
    return decorator


def background_task(func):
    @wraps(func)
    async def wrapper():
        await client.wait_until_ready()
        await func()

    client.loop.create_task(wrapper())
    return wrapper


def on_event(event_name):
    def decorator(func):
        if event_name not in bot.events.keys():
            raise LinkBotError("For method {}, {} is not a registered event.".format(func.__name__, event_name))
        else:
            bot.events[event_name].append(func)
        return func
    return decorator


def command(syntax, description, examples, aliases=None, show_in_help=True, help_subcommand=True):
    aliases = aliases or []
    def decorator(func):
        @wraps(func)
        async def wrapper(cmd: Command, *args, **kwargs):
            if help_subcommand and len(cmd.args) > 0 and cmd.args[0] == 'help':
                from linkbot.commands import help
                cmd.args = [cmd.command_arg]
                cmd.argstr = cmd.command_arg
                await help(cmd)
            else:
                logging.info("Running command: {}".format(func.__name__))
                await func(cmd, *args, **kwargs)
                logging.info("Command complete: {}".format(func.__name__))

        cmd_info = CommandInfo(func.__name__, wrapper, syntax, description, examples, aliases, show_in_help)
        bot.commands[func.__name__] = cmd_info
        for a in aliases:
            bot.commands[a] = cmd_info
        return wrapper
    return decorator


def _usrepl(s):
    return s.replace('_', ' ')
