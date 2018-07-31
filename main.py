import logging
from linkbot.bot import bot


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(processName)-10s] %(message)s')


if __name__ == "__main__":
    bot.run()