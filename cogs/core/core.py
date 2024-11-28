from typing import Optional

from discord.ext import commands
from discord.ext.commands import Context

from core.utils.message import Messenger
from core.utils.cog import Cog

class Core(Cog, description='A category for core-functions, owner-only'):

    @commands.is_owner()
    @commands.command(description='Synchonizes slash commands')
    async def sync(self, ctx: Context, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to sync, none will be global')) -> None:
        synced_commands = await self.bot.tree.sync(guild=self.bot.get_guild(guild_id))
        self.bot.tree.fetched_commands = await self.bot.tree.fetch_commands()
        await Messenger(ctx).reply(f'Synchonized `{len(synced_commands)}` command(s)')
    
    @commands.is_owner()
    @commands.command(description='Unsynchonizes slash commands')
    async def desync(self, ctx: Context, guild_id: Optional[int] = commands.parameter(default=None, description='The id of the guild to unsync, none will be global')):
        await self.bot.tree.clear_commands(guild=self.bot.get_guild(guild_id))
        await self.bot.tree.sync()
        await Messenger(ctx).reply(content=f'All slash commands have been desynchonized')
    
    @commands.is_owner()
    @commands.command(description='Load cog')
    async def load(self, ctx: Context, cog: str):
        cog = cog.lower()
        messenger = Messenger(ctx)

        try:
            await self.bot.load_extension(f'cogs.{cog}')
            await messenger.reply(content=f'`{cog}` has been loaded')

        except commands.ExtensionNotFound:
            return await messenger.reply(f'{cog} is not a valid cog')
        except commands.ExtensionAlreadyLoaded:
            return await messenger.reply(f'{cog} was already loaded')

    @commands.is_owner()
    @commands.command(description='Unload cog')
    async def unload(self, ctx: Context, cog: str):
        cog = cog.lower()
        messenger = Messenger(ctx)
        if cog == 'core':
            return await messenger.reply('You can\'t unload `core` cog')

        try:
            await self.bot.unload_extension(f'cogs.{cog}')
            await messenger.reply(f'`{cog}` has been unloaded')

        except commands.ExtensionNotFound:
            return await messenger.reply(f'`{cog}` is not a valid cog')
        except commands.ExtensionNotLoaded:
            return await messenger.reply(f'`{cog}` is not loaded')
    
    @commands.is_owner()
    @commands.command(description='Shutdown the bot')
    async def shutdown(self, ctx: Context) -> None:
        await Messenger(ctx).reply('Bot is shutting down...')
        await self.bot.close()