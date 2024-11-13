from .. import Cog
from typing import Optional

from discord import Member, Role, AllowedMentions
from discord.abc import GuildChannel
from discord import app_commands
from discord import Interaction

from core.utils.message import Messenger

class Manager(Cog):

    role = app_commands.Group(name='role', description='Role utilities')

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role.command()
    async def add(self, interaction: Interaction, user: Member, role: Role, reason: Optional[str] = None):
        await user.add_roles(role, reason=reason)
        await Messenger(interaction).reply(f'**Added {role.mention} to {user.mention}**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role.command()
    async def remove(self, interaction: Interaction, user: Member, role: Role, reason: Optional[str] = None):
        await user.remove_roles(role, reason=reason)
        await Messenger(interaction).reply(f'**Removed {role.mention} from {user.mention}**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')
    
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role.command()
    async def delete(self, interaction: Interaction, role: Role, reason: Optional[str] = None):
        await role.delete(reason=reason)
        await Messenger(interaction).reply(f'**Deleted {role.name} from the server**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @app_commands.command(description='Lock a channel')
    async def lock(self, interaction: Interaction, channel: Optional[GuildChannel] = None, role: Optional[Role] = None, reason: Optional[str] = None):
        channel = channel or interaction.channel
        role = role or interaction.guild.default_role
        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        await channel.set_permissions(role, overwrite=overwrite, reason=reason)
        await Messenger(interaction).reply(content=f'**{channel.mention} has been locked**\n>>> Manager: {interaction.user.mention}\nFor: {role}\nReason: `{reason or 'No reason provided'}`', allowed_mentions=allowed_mentions)
    
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @app_commands.command(description='Unlock a channel')
    async def unlock(self, interaction: Interaction, channel: Optional[GuildChannel] = None, role: Optional[Role] = None, reason: Optional[str] = None):
        channel = channel or interaction.channel
        role = role or interaction.guild.default_role
        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = True
        await channel.set_permissions(role, overwrite=overwrite, reason=reason)
        await Messenger(interaction).reply(f'**{channel.mention} has been unlocked**\n>>> Manager: {interaction.user.mention}\nFor: {role}\nReason: `{reason or 'No reason provided'}`', allowed_mentions=allowed_mentions)
    
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @app_commands.command(name='lock-all', description='Lock all channels')
    async def lock_all(self, interaction: Interaction, role: Optional[Role] = None, reason: Optional[str] = None):
        role = role or interaction.guild.default_role
        channels = interaction.guild.channels
        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite=overwrite)
        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
        await Messenger(interaction).reply(f'**Locked {len(channels)} channels**\n>>> Manager: {interaction.user.mention}\nFor: {role}\nReason: {reason or 'No reason provided'}', allowed_mentions=allowed_mentions)
    
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @app_commands.command(name='unlock-all', description='Unlock all channels')
    async def unlock_all(self, interaction: Interaction, role: Optional[Role] = None, reason: Optional[str] = None):    
        role = role or interaction.guild.default_role
        channels = interaction.guild.channels
        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite.send_messages = True
            await channel.set_permissions(role, overwrite=overwrite)
        allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
        await Messenger(interaction).reply(f'**Unlocked {len(channels)} channels**\n>>> Manager: {interaction.user.mention}\nFor: {role}\nReason: {reason or 'No reason provided'}', allowed_mentions=allowed_mentions)
    