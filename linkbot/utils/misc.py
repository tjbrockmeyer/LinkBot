
import os
import json
from datetime import datetime
from typing import List, Any


def save_json(filepath: str, data: Any, pretty: bool=False):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=(None if not pretty else 4))


def load_json(filepath: str):
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)


def format_as_column(content: str, column_length: int, alignment: int=-1):
    add_spaces = column_length - len(content)
    if alignment == 0:
        left = add_spaces // 2
        right = add_spaces - left
        return " " * left + content + " " * right
    if alignment < 0:
        return content + " " * add_spaces
    return " " * add_spaces + content


def english_listing(items: List[Any]):
    if not items:
        return ''
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return ' and '.join(str(i) for i in items)
    return ", ".join(str(i) for i in items[:-1]) + f", and {items[-1]}"


def split_message(msgstr: str, maxlength=2000):
    while len(msgstr) > maxlength:
        split_index = msgstr.rfind('\n', 0, maxlength)
        if split_index == -1:
            split_index = msgstr.rfind(' ', 0, maxlength)
            if split_index == -1:
                split_index = maxlength
        yield msgstr[:split_index]
        msgstr = msgstr[split_index:]
    yield msgstr


def parse_date(arg1: str, arg2: str=''):
    # Try 09/02
    try:
        f = "%m/%d"
        bday = datetime.strptime(arg1, f)
    except ValueError:

        # Try 09-02
        try:
            f = "%m-%d"
            bday = datetime.strptime(arg1, f)
        except ValueError:

            # Try Sep 02
            try:
                arg1 = arg1.lower().capitalize()
                f = "%b %d"
                bday = datetime.strptime(arg1 + " " + arg2, f)
            except ValueError:

                # Try September 02
                f = "%B %d"
                bday = datetime.strptime(arg1 + " " + arg2, f)
    return bday



def create_config(filepath: str):
    with open(filepath, 'w') as cfg:
        cfg.write(r"""
# Server owner discord id
# Set this to your own id in order to use owner commands
# Owner is automatically an admin and is allowed to use admin commands as well.
# You need to know your data-side id for this, so turn on dev options in your
# user settings on discord, then right click yourself and copy your ID.
ownerDiscordId=

# Prefix for using commands with this bot.
# Preceed any command being issued to the bot with this prefix.
# commands being sent of a DM to the bot do not require this prefix.
# Default (with no quotes): "."
prefix=.

debug=False

# Information regarding the bot.
# These are all found on your discord developer page: https://discordapp.com/developers/applications
# Select your bot, and under 'General Information', clientId and clientSecret and be found.
# Under the 'Bot' tab, botToken can be found.
[bot]
token=
clientId=
clientSecret=

[apikeys]
# Key for accessing Google's API (Image search and YouTube search).
google=
# Key for accessing Riot Games' API.
riotgames=

# Information that is required in order to access the postgresql database.
[database]
# Where the neo4j server is hosted. The default connection is "bolt://localhost:7687".
uri=bolt://localhost:7687
# username/password to log into the database as. The default username is "neo4j".
username=neo4j
password=
""")
