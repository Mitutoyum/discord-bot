from .. import Cog
from typing import Optional


from discord.ext import commands
from discord.ext.commands import Context

from core.utils.message import Messenger

class Owner(Cog, description='Owner-only category'):

    @commands.is_owner()
    @commands.command(description='Synchonizes slash commands')
    async def sync(self, ctx: Context, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to sync, none will be global')) -> None:
        synced_commands = await self.bot.tree.sync(guild=self.bot.get_guild(guild_id))
        await Messenger(ctx).reply(f'Synced {len(synced_commands)} command(s)')
    
    @commands.is_owner()
    @commands.command(description='Unsynchonizes slash commands')
    async def unsync(self, ctx: Context, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to unsync, none will be global')):
        await self.bot.tree.clear_commands(guild=self.bot.get_guild(guild_id))
        await self.bot.tree.sync()
        await Messenger(ctx).reply(content=f'```All slash commands have been unsynchonized```')
    
    @commands.is_owner()
    @commands.command(description='Load cog')
    async def load(self, ctx: Context, cog: str):
        message_utils = Messenger(ctx)
        try:
            await self.bot.load_extension(f'cogs.{cog}')
            await message_utils.reply(content=f'```{cog} has been loaded```')

        except commands.ExtensionNotFound:
            return await message_utils.reply(f'{cog} is not a valid cog')
        except commands.ExtensionAlreadyLoaded:
            return await message_utils.reply(f'{cog} was already loaded')

    @commands.is_owner()
    @commands.command(description='Unload cog')
    async def unload(self, ctx: Context, cog: str):
        message_utils = Messenger(ctx)
        try:
            await self.bot.unload_extension(f'cogs.{cog}')
            await message_utils.reply(f'```{cog} has been unloaded```')

        except commands.ExtensionNotFound:
            return await message_utils.reply(f'{cog} is not a valid cog')
        except commands.ExtensionNotLoaded:
            return await message_utils.reply(f'{cog} is not loaded')
    
    @commands.is_owner()
    @commands.command(description='Shutdown the bot')
    async def shutdown(self, ctx: Context) -> None:
        await Messenger(ctx).reply('Bot is shutting down...')
        await self.bot.close()