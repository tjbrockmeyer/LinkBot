from Commands.CmdHelper import *
import threading


@command(
    ["{c}"],
    "**Owner Only** Logs the bot out.",
    [
        ("logout", "Logs the bot out.")
    ],
    aliases=['logoff'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    bot.send_message(None, None, None)
    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() \
                and thread is not threading.current_thread():
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()
    logging.info("All threads closed. Logging out.")

    await cmd.channel.send("Logging out.")
    await bot.client.logout()
