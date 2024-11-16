import discord

from typing import Optional
from datetime import datetime

from discord import app_commands, Interaction, TextChannel
from discord.abc import GuildChannel

from core.utils.message import ChannelMessenger, Messenger
from core.utils.cog import CogMixin, Cog
from core.utils import config_manager

def is_enabled(guild_id: str | int) -> bool:
    return config_manager.get_flag(f'guild.{guild_id}.modlog.is_enabled', False, check_global=False)

def get_modlog_channel(bot, guild_id: int | str) -> TextChannel:
    channel_id = config_manager.get_flag(f'guild.{guild_id}.modlog.channel', check_global=False)
    return bot.get_channel(channel_id)

class ModLog(CogMixin):

    modlog = app_commands.Group(name='modlog', description='Track server events and mod actions')

    @modlog.command()
    async def enable(self, interaction: Interaction):
        config_manager.set_flag(f'guild.{interaction.guild_id}.modlog.is_enabled', True)
        await Messenger(interaction).reply('Modlog is now enabled')

    @modlog.command()
    async def disable(self, interaction: Interaction):
        config_manager.set_flag(f'guild.{interaction.guild_id}.modlog.is_enabled', False)
        await Messenger(interaction).reply('Modlog is now disabled')

    @modlog.command(name='set-channel', description='Set the channel for logging')
    async def set_channel(self, interaction: Interaction, channel: Optional[TextChannel] = None):
        channel = channel or interaction.channel
        config_manager.set_flag(f'guild.{interaction.guild_id}.modlog.channel', channel.id)
        await Messenger(interaction).reply(f'Modlog channel is now set to {channel.mention}')
    
    @modlog.command()
    async def log(self, interaction: Interaction, event: str) -> None:
        pass #todo

    @Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel) -> None:
        guild = channel.guild
        modlog_channel = get_modlog_channel(guild.id)

        if not is_enabled(guild.id) or not modlog_channel:
            return
        
        by = (await guild.audit_logs(limit=1).__anext__()).user
        at = discord.utils.format_dt(channel.created_at)
        
        await ChannelMessenger(modlog_channel).send(f'**Modlog: {channel.mention} channel was created**\n>>> By: {by.mention}\nAt: {at}')
    
    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel) -> None:
        guild = channel.guild
        modlog_channel = get_modlog_channel(self.bot, guild.id)

        if not is_enabled(guild.id) or not modlog_channel:
            return

        by = (await guild.audit_logs(limit=1).__anext__()).user
        at = discord.utils.format_dt(datetime.now(), 'R')

        await ChannelMessenger(modlog_channel).send(f'**Modlog: `{channel.name}` was deleted**\n>>> Category: {channel.category}\nBy: {by.mention}\nAt: {at}')

    # @Cog.listener()
    # async def on_guild_channel_update(self, before, after) -> None:
    #     pass # todo