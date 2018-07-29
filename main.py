import logging
from linkbot.bot import bot


def main():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(threadName)-10s] %(message)s')
    bot.run()


if __name__ == "__main__":
    main()