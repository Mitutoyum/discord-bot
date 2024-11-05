from core.bot import Bot

from discord.ext import commands
from logging import getLogger


logger = getLogger(__name__)

__all__ = [
    'Cog'
]

class Cog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    async def cog_load(self) -> None:
        logger.info(f'Loaded {self.qualified_name} cog with {len(self.get_commands()) + len(self.get_app_commands())} commands')
