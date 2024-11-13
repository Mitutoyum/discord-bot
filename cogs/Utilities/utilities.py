from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from core.utils.message import Messenger

class Utilities(Cog):

    @commands.command()
    async def test(self, ctx: Context):
        a = ctx.guild.audit_logs(limit=1)
        print((await a.__anext__()).user)
