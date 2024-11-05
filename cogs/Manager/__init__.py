from core.bot import Bot
from .manager import Manager

async def setup(bot: Bot) -> None:
    await bot.add_cog(Manager(bot))