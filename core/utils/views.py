from typing import Optional

import discord
from discord import ButtonStyle, app_commands, ui
from discord.ext import commands
from discord.ext.commands import Bot

from . import config_manager, embeds

# from core.bot import Bot


class BaseView(ui.View):
    message: discord.Message

    def __init__(
        self,
        author: discord.User | discord.Member,
        timeout: Optional[float] = 180,
        ephemeral: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)
        self.author = author
        self.ephemeral = ephemeral
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.author == interaction.user


class ConfirmPrompt(BaseView):
    @ui.button(label="Confirm", style=ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        self.value = True
        self.stop()

    @ui.button(label="Cancel", style=ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(
            content="Cancelled.", embed=None, view=None
        )
        self.value = False
        self.stop()


class HelpCategorySelect(ui.Select):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            placeholder="Category Menu",
            options=[
                discord.SelectOption(label=name, description=cog.description)
                for name, cog in bot.cogs.items()
            ],
        )
        self.bot: Bot = bot

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        cog = self.bot.get_cog(self.values[0])
        embed = embeds.BaseEmbed(interaction.guild_id)
        embed.title = f"Showing category: `{cog.qualified_name}`"
        embed.description = f"```{cog.description or 'No description'}```"

        for command in cog.walk_commands():
            if isinstance(command, commands.Group):
                continue
            prefix = config_manager.get_flag(f"guild.{interaction.guild_id}.prefix")
            description = command.description or command.help

            embed.add_field(
                name=f"> {prefix}{command.name}", value=description, inline=False
            )

        for command in cog.walk_app_commands():
            if command.parent != None:
                continue
            embed.add_field(
                name=f"> {await self.bot.tree.get_mention(command.name)}",
                value=command.description or "",
                inline=False,
            )
        await interaction.followup.edit_message(interaction.message.id, embed=embed)
