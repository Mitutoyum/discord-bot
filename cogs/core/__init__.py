from .core import Core

from core.bot import Bot

async def setup(bot: Bot):
    await bot.add_cog(Core(bot))