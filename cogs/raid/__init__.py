from .raid import Raid
from core.bot import Bot

async def setup(bot: Bot) -> None:
    await bot.add_cog(Raid(bot))