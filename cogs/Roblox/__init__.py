from core.bot import Bot
from .main import Roblox

async def setup(bot: Bot) -> None:
    await bot.add_cog(Roblox(bot))