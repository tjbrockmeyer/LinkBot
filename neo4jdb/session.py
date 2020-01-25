import asyncio
import functools
import logging

import neo4j

import neo4jdb.driver


def try_log_query(query, **kwargs):
    if not neo4jdb.driver.LOG_QUERIES:
        return
    for k, v in kwargs.items():
        query = query.replace(f"{{{k}}}", f"{v}")
    logging.info("Neo4j Query:\n  " + query.replace('\n', '\n  '))


class Session:
    @classmethod
    async def new(cls):
        return Session(asyncio.get_running_loop())

    @classmethod
    async def tx(cls):
        return Session(asyncio.get_running_loop(), True)

    def __init__(self, loop: asyncio.AbstractEventLoop, as_tx=False):
        self.is_tx = as_tx
        self.s: neo4j.Session = neo4jdb.driver._driver.session()
        self.t: neo4j.Transaction
        self.loop = loop

    async def __aenter__(self):
        if self.is_tx:
            self.t = self.s.begin_transaction()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.is_tx:
            if exc_val is not None:
                self.t.rollback()
            else:
                self.t.commit()
        self.s.close()

    async def run(self, query: str, **kwargs) -> neo4j.BoltStatementResult:
        try_log_query(query, **kwargs)
        if self.is_tx:
            func = self.t.run
        else:
            func = self.s.run
        return await self.loop.run_in_executor(None, functools.partial(func, query, **kwargs))
