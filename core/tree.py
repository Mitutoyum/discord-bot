import discord

from core import utils, errors
from discord import Interaction
from discord.ext import commands
from discord.app_commands import CommandTree
from discord.app_commands import AppCommandError

from discord import app_commands
from core.bot import Bot


class Tree(CommandTree):
    bot: Bot = None

    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if not await utils.error_handler(interaction, error):
            await super().on_error(interaction, error)

    async def get_mention(self, command: str | commands.HybridCommand | app_commands.Command | commands.Command, *, guild: discord.abc.Snowflake | None = None) -> str | None:
        if isinstance(command, str):
            command = self.get_command(command)
        if not command:
            return None
        
        app_command = discord.utils.get(await self.fetch_commands(guild=guild), name=(command.root_parent or command).name)
        if not app_command:
            return None
        return app_command.mention
    
    async def get_cog(self, command: str | app_commands.AppCommand | app_commands.Command):
        if not isinstance(command, str):
            command = command.qualified_name

        for cog in self.bot.cogs.values():
            if discord.utils.get(cog.get_app_commands(), qualified_name=command):
                return cog
        return None