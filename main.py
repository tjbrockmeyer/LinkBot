import logging
import os
from pathlib import Path
from linkbot.bot import bot


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(processName)-10s] %(message)s')


def main():
    if os.path.isfile('INSTANCE'):
        raise EnvironmentError("Only one instance may be running at a time.")
    Path('INSTANCE').touch()
    try:
        bot.run()
    finally:
        os.remove('INSTANCE')


if __name__ == "__main__":
    main()