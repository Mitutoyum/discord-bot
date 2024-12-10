from core.bot import Bot
from .roblox import Roblox


async def setup(bot: Bot) -> None:
    await bot.add_cog(Roblox(bot))