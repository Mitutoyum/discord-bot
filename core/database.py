import aiosqlite
import sqlite3
import logging


from . import config
from asyncio import Queue
from aiosqlite import Connection
from typing import Optional, Self

tables = {
    "temp_bans": "(userid INTEGER, guild_id INTEGER, release_date TEXT)",
    "temp_mutes": "(userid INTEGER, guild_id INTEGER, release_date TEXT)",
    "warns": "(userid INTEGER, guild_id INTEGER, reason TEXT)",
}
logger = logging.getLogger(__name__)


class ConnectionPool:
    def __init__(self, maxsize: int = 0):
        self.pool = Queue(maxsize)

    async def _acquire(self) -> Connection:
        if self.pool.empty():
            connection = await aiosqlite.connect(config.database_path)
        else:
            connection = await self.pool.get()

        return connection

    def acquire(self):
        return AcquireContextManager(self)

    async def release(self, connection: Connection):
        await self.pool.put(connection)

    async def close(self) -> None:
        while not self.pool.empty():
            await (await self.pool.get()).close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


class AcquireContextManager:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool
        self.connection = None

    async def __aenter__(self) -> Connection:
        self.connection = await self.pool._acquire()
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.pool.release(self.connection)

    def __await__(self) -> Connection:
        self.connection = self.pool._acquire().__await__()
        return self.connection


def init():
    db = sqlite3.connect(config.database_path)

    with db:
        cursor = db.cursor()
        for table, column in tables.items():
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table + column}")

    db.close()
