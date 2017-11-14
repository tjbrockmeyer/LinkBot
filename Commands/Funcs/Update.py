from Commands.CmdHelper import *
from Commands.Funcs import cmd_logout
import threading
import os
import git


def cmd_update(cmd: Command):
    logging.info("Command: Update")

    if not IsOwner(cmd.author):
        SendMessage(cmd.channel, "You must be the bot owner to use this command.")
        return

    for thread in threading.enumerate():
        if thread.name == 'cmd_update':
            SendMessage(cmd.channel, "Update is already in progress.")
            return

    logging.info("Pulling to: " + os.path.curdir)
    g = git.cmd.Git(os.path.curdir)
    g.pull()
    link_bot.restart = True
    cmd_logout(cmd)
