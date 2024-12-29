from core.bot import Bot
from .moderation import Moderation

async def setup(bot: Bot) -> None:
    await bot.add_cog(Moderation(bot))