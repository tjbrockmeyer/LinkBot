import logging

from Main.Events import link_bot
from Sensitive import DISCORD_API_KEY


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s] [%(threadName)-10s] %(message)s')

    link_bot.debug = False
    link_bot.RunThreaded(DISCORD_API_KEY)

if __name__ == "__main__":
    main()