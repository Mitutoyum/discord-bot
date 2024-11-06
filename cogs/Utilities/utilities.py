from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from core.utils import MessageUtils
from discord.ext.commands import Context


class Utilities(Cog):

    @commands.command()
    async def test(self, interaction: Interaction):
        db = await self.bot.connection_pool.acquire()
        print(db)
        await db.close()
        # async with self.bot.connection_pool.acquire() as db:
        #     print('e')
        print(self.bot.connection_pool.pool.qsize())