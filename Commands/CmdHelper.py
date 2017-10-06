import logging
from Main.Bot import link_bot
from Main.Helper import SendMessage, SendErrorMessage, OnSyntaxError, IsOwner, IsAdmin


def disabled_command(reason=""):
    """Decorator used to disable usage of a command function."""
    def decorator(func):
        def wrapper(cmd):
            if reason != "":
                SendMessage(cmd.channel, "This command is currently disabled. Reason: " + reason)
            else:
                SendMessage(cmd.channel, "This command is currently disabled.")
        return wrapper
    return decorator
