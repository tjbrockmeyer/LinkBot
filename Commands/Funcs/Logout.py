from Commands.CmdHelper import *
import threading


@restrict(OWNER_ONLY)
@command
def logout(cmd: Command):
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
