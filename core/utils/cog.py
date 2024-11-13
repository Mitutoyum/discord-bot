from core.bot import Bot

from discord.ext import commands
from abc import ABCMeta

from logging import getLogger

logger = getLogger(__name__)

__all__ = [
    'Cog',
    'GroupCog',
    'CogMixin',
    'GroupCogMixin'
]

class Meta(commands.CogMeta, ABCMeta):
    pass

class Mixin(metaclass=ABCMeta):
    pass

class Cog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    async def cog_load(self) -> None:
        logger.info(f'Loaded {self.qualified_name} cog with {len(self.get_commands() + self.get_app_commands())} commands')

class GroupCog(commands.GroupCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

class CogMixin(Mixin, Cog, metaclass=Meta):
    pass