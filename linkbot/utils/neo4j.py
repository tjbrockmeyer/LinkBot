import asyncio
import time
import traceback
from concurrent import futures

import neo4j
from neo4j import GraphDatabase, basic_auth

RETRY_WAITS = [0, 1, 4]  # How long to wait after each successive failure.


class Neo4j:
    """Neo4j database API."""

    def __init__(self, config, loop: asyncio.AbstractEventLoop):
        self.driver = None
        self.config = config
        self.loop = loop
        self.executor = futures.ThreadPoolExecutor(max_workers=30)
        for retry_wait in RETRY_WAITS:
            try:
                self.init_driver()
                break
            except:
                if retry_wait == RETRY_WAITS[-1]:
                    raise
                else:
                    print('WARNING: retrying to Init DB; err:')
                    traceback.print_exc()
                    time.sleep(retry_wait)  # wait for 0, 1, 3... seconds.

    def init_driver(self):
        auth = basic_auth(self.config['user'], self.config['pass'])
        self.driver = GraphDatabase.driver(self.config['url'], auth=auth)

    async def afetch_start(self, query, **kwargs):
        session = self.driver.session(access_mode=neo4j.READ_ACCESS)
        return session, await self.loop.run_in_executor(self.executor, lambda: session.run(query, **kwargs).records())

    async def afetch_iterate(self, session, iterator):
        def iterate():
            try:
                return next(iterator)
            except StopIteration:
                return None

        while True:
            res = await self.loop.run_in_executor(self.executor, iterate)
            if res is None:
                return
            else:
                yield dict(res)

    async def afetch(self, query):
        for retry_wait in RETRY_WAITS:
            try:
                session, iter = await self.afetch_start(query)
                break
            except (BrokenPipeError, neo4j.exceptions.ServiceUnavailable) as e:
                if retry_wait == RETRY_WAITS[-1]:
                    raise
                else:
                    await asyncio.sleep(retry_wait)
                    await self.loop.run_in_executor(self.executor, self.init_driver)
        async for x in self.afetch_iterate(session, iter):
            yield x

        await self.loop.run_in_executor(self.executor, session.close)

    async def afetch_one(self, query):
        async for i in self.afetch(query):
            return i
        return None

    async def aexec(self, query):
        async for i in self.afetch(query):
            pass
        return
