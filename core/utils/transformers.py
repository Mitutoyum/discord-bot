import datetime
from discord.ext import commands
from discord.app_commands import Transformer

class DurationConverter(Transformer):
    async def transform(self, interaction: commands.Context, value: str) -> datetime.timedelta:
        multipliers = {
            's': 1,  # seconds
            'm': 60,  # minutes
            'h': 3600,  # hours
            'd': 86400,  # days
            'w': 604800  # weeks
        }
        try:
            amount = int(value[:-1])
            unit = value[-1]
            seconds = amount * multipliers[unit]
            return datetime.timedelta(seconds=seconds)
        except (ValueError, KeyError):
            raise commands.BadArgument('Invalid duration')
