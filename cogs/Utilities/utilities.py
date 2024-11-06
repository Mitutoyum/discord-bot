from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from core.utils import MessageUtils
from discord.ext.commands import Context


class Utilities(Cog):

    @commands.command()
    async def test(self, interaction: Interaction):
        pass