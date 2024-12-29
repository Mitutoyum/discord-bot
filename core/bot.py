import logging

from discord.ext import commands
from core import config, database
from core.utils.helpers import error_handler

from .tree import Tree

logger = logging.getLogger(__name__)


class Bot(commands.AutoShardedBot):
    tree: Tree  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tree.bot = self
        self.connection_pool = database.ConnectionPool()

    async def close(self) -> None:
        await self.connection_pool.close()
        await super().close()
        logger.info("Closing bot.")

    async def setup_hook(self) -> None:
        for cog in config.cogs_dir.iterdir():
            if cog.name.startswith("_") or cog.name.startswith("."):
                continue
            await self.load_extension(f"cogs.{cog.stem}")

    async def on_ready(self) -> None:
        logger.info("Bot is ready")

    async def on_command_error(
        self, ctx: commands.Context, exception: commands.CommandError
    ):
        if not await error_handler(ctx, exception):
            await super().on_command_error(ctx, exception)
