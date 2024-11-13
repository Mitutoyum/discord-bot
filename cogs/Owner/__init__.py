from .owner import Owner

from discord.ext.commands import Bot

async def setup(bot: Bot):
    await bot.add_cog(Owner(bot))