import aiosqlite
import sqlite3
import asyncio

from aiosqlite import Connection
from . import config

tables = {
    'temp_bans': '(userid INTEGER, guild_id INTEGER, release_date TEXT)'
}

connection_pool = asyncio.Queue()

async def __aenter__(self):
    return self

async def __aexit__(self, *args, **kwargs):
    await release_connection(self)

aiosqlite.Connection.__aenter__ = __aenter__
aiosqlite.Connection.__aexit__ = __aexit__
    
async def get_connection() -> Connection:
    if connection_pool.empty():
        connection = await aiosqlite.connect(config.database_path)
    else:
        connection = await connection_pool.get()
    return connection

async def release_connection(connection: Connection) -> None:
    await connection_pool.put(connection)

async def close_all():
    while not connection_pool.empty():
        await (await connection_pool.get()).close()

def init():
    with sqlite3.connect(config.database_path) as db:
        cursor = db.cursor()
        for table, column in tables.items():
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table + column}')