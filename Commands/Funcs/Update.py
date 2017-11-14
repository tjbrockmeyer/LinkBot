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
        if thread is not threading.current_thread() and (thread.name == 'cmd_update' or thread.name == 'cmd_upgrade'):
            SendMessage(cmd.channel, "Update is already in progress.")
            return

    logging.info("Pulling to: " + os.getcwd())
    g = git.cmd.Git(os.getcwd())
    g.pull('origin', 'master')
    logging.info("Pull complete.")
    SendMessage(cmd.channel, "Update complete. Restarting...")

    link_bot.restart = True
    cmd_logout(cmd)
