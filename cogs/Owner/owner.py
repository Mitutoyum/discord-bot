from .. import Cog

from discord import Interaction
from discord import app_commands
from discord.ext import commands
from core.utils import MessageUtils
from typing import Optional

class Owner(Cog, description='Owner-only category'):

    @commands.is_owner()
    @commands.command(description='Synchonizes slash commands')
    async def sync(self, interaction: Interaction, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to sync, none will be global')) -> None:
        synced_commands = await self.bot.tree.sync(guild=self.bot.get_guild(guild_id))
        await MessageUtils(interaction).reply(content=f'```Synced {len(synced_commands)} command(s)```')
    
    @commands.is_owner()
    @commands.command(description='Unsynchonizes slash commands')
    async def unsync(self, interaction: Interaction, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to unsync, none will be global')):
        await self.bot.tree.clear_commands(guild=self.bot.get_guild(guild_id))
        await self.bot.tree.sync()
        await MessageUtils(interaction).reply(content=f'```All slash commands have been unsynchonized```')
    
    @commands.is_owner()
    @app_commands.describe(cog = 'The cog the load')
    @app_commands.command(description='Load the given cog')
    async def load(self, interaction: Interaction, cog: str):
        await self.bot.load_extension(f'cogs.{cog}')
        await MessageUtils(interaction).reply(content=f'```{cog} has been loaded```')
    
    @load.autocomplete('cog')
    async def load_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.choices(name=cog.qualified_name, value=cog.qualified_name)
            for cog in self.bot.cogs.values()
        ]

    @commands.is_owner()
    @app_commands.describe(cog = 'The cog the unload')
    @app_commands.command(description='Unload the given cog')
    async def unload(self, interaction: Interaction, cog: str):
        await self.bot.unload_extension(f'cogs.{cog}')
        await MessageUtils(interaction).reply(content=f'```{cog} has been unloaded```')
    
    @unload.autocomplete('cog')
    async def unload_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.choices(name=cog.qualified_name, value=cog.qualified_name)
            for cog in self.bot.cogs.values()
        ]
    
    @commands.is_owner()
    @app_commands.command(description='Shutdown the bot')
    async def shutdown(self, interaction: Interaction) -> None:
        await MessageUtils(interaction).reply(content=f'```Bot is shutting down```')
        await self.bot.close()