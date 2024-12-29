import discord

from typing import Optional
from datetime import datetime

from discord import app_commands, Interaction, TextChannel, Role, Guild, Member, User
from discord.abc import GuildChannel

from core.utils.message import ChannelMessenger, Messenger
from core.bot import Bot
from core.utils.cog import CogMixin, Cog
from core.utils import config_manager

def is_enabled(guild_id: str | int) -> bool:
    return config_manager.get_flag(f'guild.{guild_id}.modlog.is_enabled', False, check_global=False)

def get_modlog_channel(bot: Bot, guild_id: int | str) -> TextChannel | None:
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

    @modlog.command(name='set-channel', description='Set modlog channel')
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
        modlog_channel = get_modlog_channel(self.bot, guild.id)

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

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel) -> None:
        pass

    @Cog.listener()
    async def on_guild_role_create(self, role: Role) -> None:
        pass

    @Cog.listener()
    async def on_guild_role_delete(self, role: Role) -> None:
        pass

    @Cog.listener()
    async def on_guild_role_update(self, before: Role, after: Role) -> None:
        pass

    @Cog.listener()
    async def on_guild_update(self, before: Guild, after: Guild) -> None:
        pass

    @Cog.listener()
    async def on_member_ban(self, guild: Guild, member: Member) -> None:
        pass

    @Cog.listener()
    async def on_member_unban(self, guild: Guild, user: User) -> None:
        pass

    # @Cog.listener()
    # async def on_member_join(self, member: Member) -> None:
    #     pass

    # @Cog.listener()
    # async def on_member_remove(self, member: Member) -> None:
    #     pass

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        pass