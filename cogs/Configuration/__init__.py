from .configuration import Configuration
from core.bot import Bot


async def setup(bot: Bot):
    await bot.add_cog(Configuration(bot))