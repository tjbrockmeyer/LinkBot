import logging

from Main.Events import bot


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s] [%(threadName)-10s] %(message)s')
    bot.run_threaded()


if __name__ == "__main__":
    main()