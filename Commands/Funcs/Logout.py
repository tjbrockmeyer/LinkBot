from Commands.CmdHelper import *
import threading

# log the bot out
def cmd_logout(cmd: Command):
    logging.info("Command: logout")
    if not bot.is_owner(cmd.author):
        bot.send_message(cmd.channel, "You must be the bot's owner to use this command.")
        return

    # disable cmd reading
    bot.isReadingCommands = False

    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() \
                and thread is not threading.current_thread():
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()
    logging.info("All threads closed. Logging out.")

    bot.send_message(cmd.channel, "Logging out.")
    bot.active = False
