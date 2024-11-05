from core.bot import Bot
from .info import Info

async def setup(bot: Bot) -> None:
    await bot.add_cog(Info(bot))