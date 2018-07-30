
import os
import json


DATA_DIR = 'data/'


def format_as_column(content, column_length, alignment=-1):
    """
    Returns the append string with spaces added to create a column format.

    :param alignment: The alignment of the content in the column. -1 for left, 0 for center, 1 for right.
    :type alignment: int
    :param content: String of text to be formatted.
    :type content: str
    :param column_length: Number of characters in this column.
    :type column_length: int
    :return: The newly formatted string.
    :rtype: str
    """
    add_spaces = column_length - len(content)
    if alignment == 0:
        left = add_spaces // 2
        right = add_spaces - left
        return " " * left + content + " " * right
    if alignment < 0:
        return content + " " * add_spaces
    return " " * add_spaces + content


def save_json(filepath, data, pretty=False):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=(None if not pretty else 4))


def load_json(filepath):
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)


def create_data_dir():
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)


def create_config(filepath):
    with open(filepath, 'w') as cfg:
        cfg.writelines([
            '# Server owner discord id\n',
            '# Set this to your own id in order to use owner commands\n',
            '# Owner is automatically an admin and is allowed to use admin commands as well.\n',
            '# You need to know your data-side id for this, so turn on dev options in your\n'
            '# user settings on discord, then right click yourself and copy your ID.\n',
            'ownerDiscordId=\n\n',

            "# Information regarding the bot.\n",
            "# These are all found on your discord developer page: https://discordapp.com/developers/applications\n",
            "# Select your bot, and under 'General Information', botClientId and botClientSecret and be found.\n",
            "# Under the 'Bot' tab, botToken can be found.\n",
            "botToken=\n",
            "botClientId=\n",
            "botClientSecret=\n\n",

            "# Key for accessing Riot Games' API.\n",
            "riotApiKey=\n",
            "# Key for accessing Google's API (Image search and YouTube search).\n",
            "googleApiKey=\n\n",

            "# Prefix for using commands with this bot.\n",
            "# Preceed any command being issued to the bot with this prefix.\n",
            "# commands being sent of a DM to the bot do not require this prefix.\n",
            "# Default (with no quotes): \"link.\"\n"
            "prefix=link.\n\n",

            "debug=False\n",
        ])


def split_message(msgstr, maxlength=2000):
    if len(msgstr) <= maxlength:
        yield msgstr
    else:
        while len(msgstr) > maxlength:
            split_index = msgstr.rfind('\n', 0, maxlength)
            if split_index == -1:
                split_index = msgstr.rfind(' ', 0, maxlength)
                if split_index == -1:
                    split_index = maxlength
            msgstr = msgstr[split_index:]
            yield msgstr[:split_index]


async def send_split_message(target, message, maxlength=2000):
    for msg in split_message(message, maxlength):
        await target.send(msg)
