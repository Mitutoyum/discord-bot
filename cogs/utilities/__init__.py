from core.bot import Bot
from .utilities import Utilities

async def setup(bot: Bot) -> None:
    await bot.add_cog(Utilities(bot))