from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from core.utils.helpers import MessageUtils




class Utilities(Cog):

    @app_commands.command()
    async def test(self, interaction: Interaction):
        await MessageUtils(interaction).reply(f'**{'llllllll'} has been muted**\n>>> Moderator: {interaction.user.mention}\nDuration: {'e'}\nReason: {'l' or 'No reason provided'}')
