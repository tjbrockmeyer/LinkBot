from Commands.CmdHelper import *
import threading

# log the bot out
def cmd_logout(cmd: Command):
    logging.info("Command: logout")
    if not IsOwner(cmd.author):
        SendMessage(cmd.channel, "You must be the bot's owner to use this command.")
        return

    # disable cmd reading
    link_bot.isReadingCommands = False

    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() \
                and thread is not threading.current_thread():
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()
    logging.info("All threads closed. Logging out.")

    SendMessage(link_bot.owner, "Logging out.")
    link_bot.active = False
