
import os
import json


def format_as_no_spaces(string):
    """
    Returns the same string, but with no spaces in it.

    :param string: The string to remove spaces from.
    :type string: str
    :return: The string with no spaces.
    :rtype: str
    """
    return ''.join(string.split())


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


def find_user_in_servers(servers, user_id):
    for server in servers:
        for member in server.members:
            if member.id == user_id:
                return member
    return None


def read_config(filepath):
    options = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            index = line.find('=')
            if index == -1 or len(line[:index]) == 0 or len(line[index:]) == 0:
                print('Valid config lines must be in the form of "key=value".')
                continue
            options[line[:index]] = line[index + 1:]
    return options


def save_json(filepath, data, pretty=False):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=(None if not pretty else 4))


def load_json(filepath):
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)
