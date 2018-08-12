
from contextlib import contextmanager
import psycopg2 as psql
from linkbot.utils.ini import Ini
from typing import Type, List, Tuple


_db_connect_string = None


@contextmanager
def connect():
    with psql.connect(_db_connect_string) as conn:
        with conn.cursor() as cur:
            yield (conn, cur)


def setup(config_file: str) -> bool:
    """ Setup the connection string and test the connection. Returns True on successful setup. """

    options = Ini.load(config_file)
    db_connect = [options.get('database.hostname'), options.get('database.name'),
                  options.get('database.user'), options.get('database.password')]
    if None in db_connect:
        return False
    global _db_connect_string
    _db_connect_string = "host='{}' dbname='{}' user='{}' password='{}'".format(*db_connect)
    return True
