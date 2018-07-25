import logging
from Main.LinkBot import bot, LinkBotError
from Commands.Command import Command


def disabled_command(reason=""):
    """Decorator used to disable usage of a command function."""
    def decorator(func):
        def wrapper(cmd):
            if reason != "":
                bot.send_message(cmd.channel, "This command is currently disabled. Reason: " + reason)
            else:
                bot.send_message(cmd.channel, "This command is currently disabled.")
        return wrapper
    return decorator
