
import logging
import asyncio
import discord
from Main.LinkBot import bot, LinkBotError
from Commands.Command import Command
from functools import wraps


DISABLE = 1
ADMIN_ONLY = 2
OWNER_ONLY = 4
SERVER_ONLY = 8
DM_ONLY = 16


def restrict(conditions, reason=''):
    def passes_conditions(cmd, func):
        if DISABLE & conditions != 0:
            bot.send_message(cmd.channel, "`{}` is disabled. {}"
                             .format(_usrepl(func.__name__), "Reason: {}.".format(reason) if reason != '' else ''))
        elif OWNER_ONLY & conditions != 0 and not bot.is_admin(cmd.author):
            bot.send_message(cmd.channel, "`{}` can only be used by the bot's owner: {}"
                             .format(_usrepl(func.__name__), bot.owner))
        elif ADMIN_ONLY & conditions != 0 and not bot.is_admin(cmd.author):
            bot.send_message(cmd.channel, "`{}` can only be used by registered adnims. See `{}admin list`"
                             .format(_usrepl(func.__name__), bot.prefix))
        elif SERVER_ONLY & conditions != 0 and cmd.guild is None:
            bot.send_message(cmd.channel, "`{}` can only be used in a server."
                             .format(_usrepl(func.__name__)))
        elif DM_ONLY & conditions != 0 and not cmd.is_dm:
            bot.send_message(cmd.channel, "`{}` can only be used in a direct message."
                             .format(_usrepl(func.__name__)))
        else:
            return True
        return False

    def decorator(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            if passes_conditions(cmd, func):
                await func(cmd, *args, **kwargs)
        return wrapper
    return decorator


def require_args(count):
    def sufficient_args(cmd, func):
        if len(cmd.args) < count:
            cmd.on_syntax_error(
                "At least {} {} necessary.".format(count, 'arg is' if count == 1 else 'args are'),
                cmd_name=_usrepl(func.__name__))
            return False
        return True

    def decorator(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            if sufficient_args(cmd, func):
                await func(cmd, *args, **kwargs)
        return wrapper
    return decorator


def updates_database(func):
    @wraps(func)
    async def wrapper(cmd, *args, **kwargs):
        await func(cmd, *args, **kwargs)
        bot.save_data()
    return wrapper


def command(func):
    @wraps(func)
    async def wrapper(cmd, *args, **kwargs):
        logging.info("Running command: {}".format(func.__name__))
        await func(cmd, *args, **kwargs)
        logging.info("Command complete: {}".format(func.__name__))
    return wrapper


def on_event(event_name):
    def decorator(func):
        if event_name not in bot.events.keys():
            raise LinkBotError("For method {}, {} is not a registered event.".format(func.__name__, event_name))
        else:
            bot.events[event_name].append(func)
        return func
    return decorator


def _usrepl(s):
    return s.replace('_', ' ')
