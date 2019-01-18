import logging


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(processName)-10s] %(message)s')


if __name__ == "__main__":
    try:
        from linkbot.bot import bot, client
        bot.run()
    except Exception as e:
        logging.fatal(e)
        logging.fatal("ABORT")
