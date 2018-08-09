
import os
import json
from functools import reduce


def save_json(filepath, data, pretty=False):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=(None if not pretty else 4))


def load_json(filepath):
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)


def format_as_column(content, column_length, alignment=-1):
    add_spaces = column_length - len(content)
    if alignment == 0:
        left = add_spaces // 2
        right = add_spaces - left
        return " " * left + content + " " * right
    if alignment < 0:
        return content + " " * add_spaces
    return " " * add_spaces + content


def english_listing(items):
    if not items:
        return ''
    if len(items) == 1:
        return str(items[0])
    return reduce(lambda x, y: "{}, {}".format(y, x), reversed(items[:-1]) , "and {}".format(items[-1]))


def split_message(msgstr, maxlength=2000):
    while len(msgstr) > maxlength:
        split_index = msgstr.rfind('\n', 0, maxlength)
        if split_index == -1:
            split_index = msgstr.rfind(' ', 0, maxlength)
            if split_index == -1:
                split_index = maxlength
        yield msgstr[:split_index]
        msgstr = msgstr[split_index:]
    yield msgstr


async def send_split_message(target, message, maxlength=2000):
    for msg in split_message(message, maxlength):
        await target.send(msg)


def create_config(filepath):
    with open(filepath, 'w') as cfg:
        cfg.write(r"""
# Server owner discord id,
# Set this to your own id in order to use owner commands,
# Owner is automatically an admin and is allowed to use admin commands as well.,
# You need to know your data-side id for this, so turn on dev options in your
# user settings on discord, then right click yourself and copy your ID.,
ownerDiscordId=

# Prefix for using commands with this bot.,
# Preceed any command being issued to the bot with this prefix.,
# commands being sent of a DM to the bot do not require this prefix.,
# Default (with no quotes): \"link.\"
prefix=link.

debug=False

# Information regarding the bot.,
# These are all found on your discord developer page: https://discordapp.com/developers/applications,
# Select your bot, and under 'General Information', clientId and clientSecret and be found.
# Under the 'Bot' tab, botToken can be found.
[bot]
token=
clientId=
clientSecret=

[apikeys]
# Key for accessing Riot Games' API.,
google=
# Key for accessing Google's API (Image search and YouTube search).,
riotgames=

# Information that is required in order to access the postgresql database.
[database]
# Where the postgres server is hosted.
hostname=
# The name of the database to use.
name=
# User/pass to log into postgres as. Should have owner rights to the database.
user=
password=
""")
