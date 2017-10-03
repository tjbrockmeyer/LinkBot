from Commands.CmdHelper import *
import threading

# log the bot out
def cmd_logout(cmd):
    logging.info("Command: logout")
    link_bot.requestedStop = True  # prevent a restart
    if not IsOwner(cmd.author):
        SendMessage(cmd.channel, "You must be the bot's owner to use this command.")
        return

    # disable cmd reading
    link_bot.isStopping = True

    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() and thread.name != 'cmd_logout':
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()

    SendMessage(link_bot.owner, "Logging out.")
    link_bot.active = False
