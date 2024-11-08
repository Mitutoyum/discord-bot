from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from core.utils.helpers import MessageUtils




class Utilities(Cog):

    @app_commands.command()
    async def test(self, interaction: Interaction):
        print(interaction.response)
        await interaction.message.reply('lol')