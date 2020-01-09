import asyncio
import logging
from functools import wraps
from typing import Optional, List, Tuple

import linkbot.utils.emoji as emoji
from linkbot.bot import client
from linkbot.errors import *
from linkbot.utils.checks import *
from linkbot.utils.command import Command, CommandInfo

DISABLE = 1
SERVER_ONLY = 2
OWNER_ONLY = 4
ADMIN_ONLY = 8
DM_ONLY = 16


def restrict(conditions, reason=''):
    if conditions & ADMIN_ONLY:
        conditions |= SERVER_ONLY

    def decorator(func):
        fname = func.__name__.replace('_', ' ')

        @wraps(func)
        async def wrapper(cmd: Command, *args, **kwargs):
            if DISABLE & conditions:
                raise CommandPermissionError(
                    cmd, f"`{fname}` is disabled. {'Reason: {}.'.format(reason) if reason else ''}")
            elif OWNER_ONLY & conditions and not is_bot_owner(cmd.author):
                raise CommandPermissionError(
                    cmd, f"`{fname}` can only be used by the bot's owner: {bot.owner}")
            elif SERVER_ONLY & conditions and cmd.guild is None:
                raise CommandPermissionError(
                    cmd, f"`{fname}` can only be used in a server.")
            elif ADMIN_ONLY & conditions and not await is_admin(cmd.author):
                raise CommandPermissionError(
                    cmd, f"`{fname}` can only be used by registered admins. See `{bot.prefix}admin list`")
            elif DM_ONLY & conditions and not cmd.is_dm:
                raise CommandPermissionError(
                    cmd, f"`{fname}` can only be used in a direct message.")
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
                    cmd, reason=f"At least {count} argument{' is' if count == 1 else 's are'} necessary.")
            await func(cmd, *args, **kwargs)

        return wrapper

    return decorator


def on_event(event_name):
    # For a list of usable events, see each event decorated with the 'event' decorator in bot.py.
    def decorator(func):
        if event_name not in bot.events.keys():
            raise LinkBotError(f"For method {func.__name__}, {event_name} is not a registered event.")
        else:
            bot.events[event_name].append(func)
        return func

    return decorator


def command(syntax: List[str],
            description: str,
            examples: List[Tuple[str, str]], *,
            name: str = "",
            aliases: Optional[List[str]] = None,
            show_in_help: bool = True,
            help_subcommand: bool = True):
    def decorator(func):
        a: List[str] = aliases or []
        n: str = name or func.__name__

        @wraps(func)
        async def wrapper(cmd: Command, *args, **kwargs):
            if help_subcommand and cmd.args and cmd.args[0] == 'help':
                from linkbot.commands.cmd_help import send_help
                cmd.args = [cmd.command_arg]
                cmd.argstr = cmd.command_arg
                await send_help(cmd.channel, cmd.command_arg)
            else:
                logging.info(f"Running command: {n}")
                future = asyncio.ensure_future(func(cmd, *args, **kwargs), loop=client.loop)
                e = (await asyncio.gather(future, loop=client.loop, return_exceptions=True))[0]
                logging.info(f"Command complete: {n}")

                if e:
                    if not issubclass(type(e), CommandError):
                        await cmd.channel.send(embed=bot.embed(
                            discord.Color.red(),
                            title=f"{emoji.Symbol.exclamation} Unknown Error {emoji.Symbol.exclamation}",
                            description="Whoops! Something went wrong.\n"
                                        "Your command could not be completed.\n"
                                        "An error report was automatically sent."))
                    raise e

        cmd_info = CommandInfo(n, wrapper, syntax, description, examples, a, show_in_help)
        bot.commands[n] = cmd_info
        for x in a:
            bot.commands[x] = cmd_info
        return wrapper

    return decorator
