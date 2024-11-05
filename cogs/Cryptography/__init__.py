from core.bot import Bot
from .cryptography import Cryptography

async def setup(bot: Bot):
    await bot.add_cog(Cryptography(bot))