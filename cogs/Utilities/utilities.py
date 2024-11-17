from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import Context
from core.utils.message import Messenger
from core.utils.cog import Cog
from core.utils import config_manager

from typing import Literal

class Utilities(Cog):

    @commands.command()
    async def test(self, ctx: Context):
        await Messenger(ctx).reply('Hello world')