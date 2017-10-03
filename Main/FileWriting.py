import os
from datetime import datetime

from Main.Helper import *

DATA_FOLDER = 'data/'
CONFIG_FILE = 'config.cfg'
SUGGESTION_FILE = 'suggestions.txt'
ADMIN_FILE = 'admins.txt'
QUOTES_FILE = 'quotes.txt'
BIRTHDAYS_FILE = 'birthdays.txt'


# create a default config file with documentation.
def create_config():
    with link_bot.lock:
        with open(DATA_FOLDER + CONFIG_FILE, 'w') as cfg:
            cfg.writelines(['# Server owner discord id\n',
                            '# Set this to your own id in order to use owner commands\n',
                            '# Owner is automatically an admin and is allowed to use admin commands as well.\n',
                            '# You need to know your data-side id for this, run the bot and use: {prefix}IDof @mention\n'])
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


def save_admins():
    with link_bot.lock:
        with open(DATA_FOLDER + ADMIN_FILE, 'w') as admins:
            for s, alist in link_bot.admins.items():
                for a in alist:
                    # save as: server;admin
                    admins.write(s + ';' + a + '\n')
    logging.info("Saved admin file.")


def load_admins():
    with link_bot.lock:
        if os.path.isfile(DATA_FOLDER + ADMIN_FILE):
            with open(DATA_FOLDER + ADMIN_FILE, 'r') as admins:
                for line in admins:
                    a = line.strip().split(';')
                    if a[0] not in link_bot.admins.keys():
                        link_bot.admins[a[0]] = list()
                    link_bot.admins[a[0]].append(a[1])
            logging.info("Loaded admins from file.")


def save_quotes():
    with link_bot.lock:
        with open(DATA_FOLDER + QUOTES_FILE, 'w') as quotes:
            for s, qlist in link_bot.quotes.items():
                for q in qlist:
                    # save as: server;author;quote
                    quotes.write(s + ';' + q[0] + ';' + q[1] + '\n')
    logging.info("Saved quote file.")


def load_quotes():
    with link_bot.lock:
        if os.path.isfile(DATA_FOLDER + QUOTES_FILE):
            with open(DATA_FOLDER + QUOTES_FILE, 'r') as quotes:
                for line in quotes:
                    q = line.strip().split(';')
                    if q[0] not in link_bot.quotes:
                        link_bot.quotes[q[0]] = list()
                    link_bot.quotes[q[0]].append((q[1], q[2]))
            logging.info("Quotes loaded from file.")


def save_birthdays():
    with link_bot.lock:
        with open(DATA_FOLDER + BIRTHDAYS_FILE, 'w') as birthdays:
            for s, pb in link_bot.birthdays.items():
                for p, b in pb.items():
                    # save as: server;author;quote
                    birthdays.write(s + ';' + p + ';' + b.strftime("%m/%d") + '\n')
    logging.info("Saved birthday file.")


def load_birthdays():
    with link_bot.lock:
        if os.path.isfile(DATA_FOLDER + BIRTHDAYS_FILE):
            with open(DATA_FOLDER + BIRTHDAYS_FILE, 'r') as birthdays:
                for line in birthdays:
                    b = line.strip().split(';')
                    # b = server id, person name, birthday
                    if b[0] not in link_bot.birthdays:
                        link_bot.birthdays[b[0]] = dict()
                    link_bot.birthdays[b[0]][b[1]] = datetime.strptime(b[2], "%m/%d")
            logging.info("Birthdays loaded from file.")