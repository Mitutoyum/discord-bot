import discord

from typing import List

from .utils.helpers import error_handler
from discord import Interaction
from discord.ext import commands
from discord.app_commands import CommandTree
from discord.app_commands import AppCommandError

from discord import app_commands
from discord.ext.commands import AutoShardedBot


class Tree(CommandTree):
    bot: AutoShardedBot = None
    fetched_commands: List[app_commands.AppCommand] = None

    async def on_error(self, interaction: Interaction, error: AppCommandError):
        if not await error_handler(interaction, error):
            await super().on_error(interaction, error)

    async def get_mention(self, command: str | commands.HybridCommand | app_commands.Command | commands.Command, *, guild: discord.abc.Snowflake | None = None) -> str | None:
        if isinstance(command, str):
            command = self.get_command(command)
            if not command:
                return None
            

        self.fetched_commands = self.fetched_commands or await self.fetch_commands(guild=guild) # for faster processing


        app_command = discord.utils.get(self.fetched_commands, name=(command.root_parent or command).name)
        if not app_command:
            return None
        return app_command.mention
    
    async def get_cog(self, command: str | app_commands.AppCommand | app_commands.Command):
        if not isinstance(command, str):
            command = command.qualified_name

        for cog in self.bot.cogs.values():
            if discord.utils.get(cog.get_app_commands(), qualified_name=command):
                return cog
        return None()