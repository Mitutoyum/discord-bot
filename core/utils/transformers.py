import datetime
from discord.ext import commands
from discord.app_commands import Transformer

class DurationTransformer(Transformer):
    async def transform(self, interaction: commands.Context, value: str) -> datetime.timedelta:
        multipliers = {
            's': 1, # second
            'm': 60, # minute
            'h': 3600, # hour
            'd': 86400, # day
            'w': 604800, # week
            'm': 2628000 # month
        }
        try:
            amount = int(value[:-1])
            unit = value[-1]
            seconds = amount * multipliers[unit]
            return datetime.timedelta(seconds=seconds)
        except (ValueError, KeyError):
            raise commands.BadArgument(f'Invalid duration')
