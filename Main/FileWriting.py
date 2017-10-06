import os
import json

from Main.Helper import *

DATA_FOLDER = 'data/'
CONFIG_FILE = 'config.txt'
SUGGESTION_FILE = 'suggestions.txt'
DATA_FILE = 'database.json'


# create a default config file with documentation.
def create_config():
    with link_bot.lock:
        if not os.path.isdir('data'):
            os.mkdir('data')
        with open(DATA_FOLDER + CONFIG_FILE, 'w') as cfg:
            cfg.writelines(['# Server owner discord id\n',
                            '# Set this to your own id in order to use owner commands\n',
                            '# Owner is automatically an admin and is allowed to use admin commands as well.\n',
                            '# You need to know your data-side id for this, so turn on dev options in your\n'
                            '# user settings on discord, then right click yourself and copy your ID.\n'])
            cfg.write('ownerDiscordId=\n\n')
            cfg.writelines(['# Prefix for using commands with this bot.\n',
                            '# Preceed any command being issued to the bot with this prefix.\n',
                            '# Commands being sent of a DM to the bot do not require this prefix.\n',
                            '# Default (with no quotes): "link."\n'])
            cfg.write('prefix=link.\n\n')
            cfg.writelines(['# NSFW option for google image search.\n',
                            '# Set to 0 for safe, set to 1 for nsfw ALLOWED.\n'])
            cfg.write('nsfw=0\n\n')
    logging.info('Created config file.')


# update the config file with the current settings
def update_config():
    with link_bot.lock:

        # if the config file doesn't exist, create it with the defaults.
        if not os.path.isfile(DATA_FOLDER + CONFIG_FILE):
            create_config()

        # read config file and write to a new one. Do this by renaming the first, then making a new one.
        os.rename(DATA_FOLDER + CONFIG_FILE, DATA_FOLDER + '~' + CONFIG_FILE)
        with open(DATA_FOLDER + '~' + CONFIG_FILE, 'r') as cfg_r, open(DATA_FOLDER + CONFIG_FILE, 'w') as cfg_w:
            for line in cfg_r:

                line = line.lstrip()  # strip whitespace on the left side.
                if len(line) == 0 or line[0] == '#':  # skip any lines that are comments.
                    cfg_w.write(line)

                elif line.startswith('ownerDiscordId='):
                    w = line[:len('ownerDiscordId=')].rstrip() + link_bot.owner.id + '\n'
                    cfg_w.write(w)

                elif line.startswith('prefix='):
                    w = line[:len('prefix=')].rstrip() + link_bot.prefix + '\n'
                    cfg_w.write(w)

                elif line.startswith('nsfw='):
                    w = line[:len('nsfw=')].rstrip() + '1' if link_bot.nsfw else '0'
                    cfg_w.write(w)

                else:
                    logging.info("Unrecognized identifier in {0}: {1}".format(CONFIG_FILE, line))

                # move to the next line.
                cfg_w.write('\n')

        # delete the copy of our original config file.
        os.remove(DATA_FOLDER + '~' + CONFIG_FILE)
    logging.info('Updated config file.')


# read the config file and save the setting into the current program state
def load_config():
    with link_bot.lock:
        if not os.path.isfile(DATA_FOLDER + CONFIG_FILE):  # if the config file doesn't exist, create it with the defaults.
            create_config()

        # read everything from the config file.
        with open(DATA_FOLDER + CONFIG_FILE, 'r') as cfg:
            for line in cfg:
                line = line.lstrip()  # strip whitespace on the left side.
                if len(line) == 0 or line[0] == '#':  # skip any lines that are comments.
                    continue

                if line.startswith('ownerDiscordId='):  # check for an identifier
                    line = line[len('ownerDiscordId='):].rstrip()  # cut off the identifier

                    found = False
                    for server in link_bot.discordClient.servers:
                        for member in server.members:  # iterate through servers that bot is a part of.
                            if member.id == line:  # if the member has the same id as provided in the config file,
                                link_bot.owner = member  # set the member as the bot's owner.
                                found = True
                                break
                        if found:
                            break
                    else:
                        logging.info("Could not find ownerDiscordId in the members of any server that I'm a part of.")

                elif line.startswith('prefix='):
                    link_bot.prefix = line[len('prefix='):].rstrip()

                elif line.startswith('nsfw='):
                    if line[len('nsfw=')].rstrip() == '1':
                        link_bot.nsfw = True
                    elif line[len('nsfw=')].rstrip() == '0':
                        link_bot.nsfw = False
                    else:
                        logging.info("Setting [nsfw] can only have values '0' or '1'.")
                        logging.info("Defaulting [nsfw] to DISABLED.")
                        link_bot.nsfw = False

                else:
                    logging.info("Unrecognized identifier/key-value pair: {0}".format(line))

            if link_bot.owner is None:
                logging.info("Owner commands are disabled.")
                logging.info("Be sure that ownerDiscordId has been supplied in {0} and that it is correct.".format(CONFIG_FILE))
    logging.info('Read from and saved contents of config file.')


def save_data():
    with link_bot.lock:
        with open(DATA_FOLDER + DATA_FILE, 'w') as f:
            json.dump(link_bot.data, f)
        logging.info("Database updated.")


def load_data():
    with link_bot.lock:
        if os.path.isfile(DATA_FOLDER + DATA_FILE):
            with open(DATA_FOLDER + DATA_FILE, 'r') as f:
                link_bot.data = json.load(f)
            logging.info("Database loaded.")