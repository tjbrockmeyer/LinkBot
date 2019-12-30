import logging

import neo4j
from neobolt.exceptions import AuthError, ServiceUnavailable

from linkbot.utils.ini import Ini

_driver: neo4j.Driver = None
LOG_QUERIES = True


def startup(config_file: str) -> bool:
    """ Setup the connection string and test the connection. Returns True on successful setup. """

    options = Ini.load(config_file)
    global _driver
    try:
        _driver = neo4j.Driver(
            options.str("database.uri"),
            auth=(options.str("database.username"), options.str("database.password")))
    except KeyError as e:
        logging.error(f"Missing key in {config_file}: {e}")
        return False
    except ServiceUnavailable:
        logging.error("The Neo4j database is currently unavailable")
        return False
    except AuthError:
        logging.error("Invalid login credentials")
        return False
    return True


def shutdown():
    if _driver:
        _driver.close()
