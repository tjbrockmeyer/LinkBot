from Commands.CmdHelper import *
from Commands.Funcs import logout
import threading
import os
import git


@command(
    ["{c}"],
    "**Owner Only** Updates the bot to the newest version, then restarts.",
    [
        ("{c}", "Downloads the latest update and restarts the bot.")
    ],
    aliases=['upgrade'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def update(cmd: Command):
    for thread in threading.enumerate():
        if thread is not threading.current_thread() and (thread.name == 'cmd_update' or thread.name == 'cmd_upgrade'):
            bot.send_message(cmd.channel, "Update is already in progress.")
            return

    logging.info("Pulling to: " + os.getcwd())
    g = git.cmd.Git(os.getcwd())
    try:
        g.pull('origin', 'master')
    except:
        logging.info("The local repository has unpushed changes.")
        if len(cmd.args) > 0 and cmd.args[0].startswith('f'):
            logging.info("Forcing an overwrite.")
            g.fetch('--all')
            g.reset('--hard', 'origin/master')
            g.pull('origin', 'master')
        else:
            bot.send_message(cmd.channel,
                        "There are unpushed changes in the local repository. Use 'update force' to force an overwrite.")
            return
    logging.info("Pull complete.")
    bot.send_message(cmd.channel, "Update complete. Restarting...")
    bot.restart = True
    logout(cmd)
