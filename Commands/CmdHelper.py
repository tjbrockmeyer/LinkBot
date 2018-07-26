
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
    def decorator(func):
        def passes_conditions(cmd):
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

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(cmd, *args, **kwargs):
                if passes_conditions(cmd):
                    await func(cmd, *args, **kwargs)
            return wrapper
        else:
            @wraps(func)
            def wrapper(cmd, *args, **kwargs):
                if passes_conditions(cmd):
                    func(cmd, *args, **kwargs)
            return wrapper

    return decorator


def require_args(count):
    def decorator(func):
        def args_good(cmd):
            if len(cmd.args) < count:
                cmd.on_syntax_error(
                    "At least {} {} necessary.".format(count, 'arg is' if count == 1 else 'args are'),
                    cmd_name=_usrepl(func.__name__))
                return False
            return True

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(cmd, *args, **kwargs):
                if args_good(cmd):
                    await func(cmd, *args, **kwargs)
            return wrapper
        else:
            @wraps(func)
            def wrapper(cmd, *args, **kwargs):
                if args_good(cmd):
                    func(cmd, *args, **kwargs)
            return wrapper
    return decorator


def updates_database(func):
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            await func(cmd, *args, **kwargs)
            bot.save_data()
    else:
        @wraps(func)
        def wrapper(cmd, *args, **kwargs):
            func(cmd, *args, **kwargs)
            bot.save_data()
    return wrapper


def command(func):
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(cmd, *args, **kwargs):
            logging.info("Running command: {}".format(func.__name__))
            await func(cmd, *args, **kwargs)
            logging.info("Command complete: {}".format(func.__name__))
    else:
        @wraps(func)
        def wrapper(cmd, *args, **kwargs):
            logging.info("Running command: {}".format(func.__name__))
            func(cmd, *args, **kwargs)
            logging.info("Command complete: {}".format(func.__name__))
    return wrapper


def _usrepl(s):
    return s.replace('_', ' ')
