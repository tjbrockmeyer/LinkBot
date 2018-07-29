


class LinkBotError(Exception):
    """ Base exception for LinkBot. """
    def __init__(self, reason):
        Exception.__init__(self, reason)

class InitializationError(LinkBotError):
    """ For errors that occur while trying to initialize LinkBot. THESE ERRORS ARE FATAL. """
    pass

class EventError(LinkBotError):
    """ For errors that occur during an event. """
    pass


class CommandError(LinkBotError):
    """ Base exception for errors related to commands. Also used for general command errors. """
    def __init__(self, cmd, reason):
        LinkBotError.__init__(self, reason)
        self.cmd = cmd

class DeveloperError(CommandError):
    """ For errors that may require developer attention. """
    def __init__(self, cmd, reason, public_reason='An unknown error occurred.'):
        CommandError.__init__(self, cmd, reason)
        self.public_reason = public_reason

class CommandPermissionError(CommandError):
    """ For errors that occur due to the command author not having the required permissions. """
    pass

class CommandSyntaxError(CommandError):
    """ For errors that occur because of an incorrectly formatted command. """
    pass
