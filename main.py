import discord

from core.bot import Bot
from core.tree import Tree
from dotenv import load_dotenv
from core import database, config
from core.utils import config_manager
from core.utils.helpers import get_prefix

import logging
from asyncio import run
from sys import exit
from os import getenv

handler = logging.FileHandler("discord.log", "w", "utf-8")
handler.setFormatter(
    logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", "{"
    )
)

discord.utils.setup_logging()
logging.root.addHandler(handler)


logger = logging.getLogger(__name__)


async def main():
    config.init()
    database.init()

    if not config_manager.get_flag("global.prefix", add_if_not_exist=False):
        exit("Missing prefix, please set one in resources/config.json")

    if status := config_manager.get_flag("global.status"):
        status = discord.Status[status]  # type: ignore

    if activity := config_manager.get_flag("global.activity"):
        activity_type = discord.ActivityType[activity["type"]]
        activity.pop("type")
        activity = discord.Activity(type=activity_type, **activity)

    bot = Bot(
        command_prefix=get_prefix,
        intents=config.intents,
        tree_cls=Tree,
        help_command=None,
        activity=activity,
        status=status,
    )

    load_dotenv()

    try:
        await bot.start(getenv("BOT_TOKEN"))  # type: ignore
    except KeyboardInterrupt:
        await bot.close()


if __name__ == "__main__":
    run(main())
