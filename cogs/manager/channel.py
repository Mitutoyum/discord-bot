from typing import Optional

from discord import (
    app_commands,
    Interaction,
    TextChannel,
    Role,
    AllowedMentions,
    ChannelType,
    ForumChannel,
)
from discord.abc import GuildChannel

from core.utils.cog import CogMixin
from core.utils.message import Messenger


class Channel(CogMixin):
    channel_group = app_commands.Group(name="channel", description="Channel management")

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @channel_group.command(description="Lock channel")  # type: ignore
    async def lock(
        self,
        interaction: Interaction,
        channel: Optional[GuildChannel] = None,
        role: Optional[Role] = None,
        reason: Optional[str] = None,
    ):
        channel: GuildChannel = channel or interaction.channel  # type: ignore
        role = role or interaction.guild.default_role  # type: ignore

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        overwrite.connect = False

        if channel.type == ChannelType.forum:
            overwrite.create_threads = False  # type: ignore

        await channel.set_permissions(role, overwrite=overwrite, reason=reason)
        await Messenger(interaction).reply(
            f"""
            **{channel.mention} has been locked**
            >>> Manager: {interaction.user.mention}
            For: {role}
            Reason: `{reason or 'No reason provided'}`
            """,
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False),
        )

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @channel_group.command(description="Unlock channel")  # type: ignore
    async def unlock(
        self,
        interaction: Interaction,
        channel: Optional[GuildChannel] = None,
        role: Optional[Role] = None,
        reason: Optional[str] = None,
    ):
        channel: GuildChannel = channel or interaction.channel  # type: ignore
        role = role or interaction.guild.default_role  # type: ignore

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None
        overwrite.connect = None

        if channel.type == ChannelType.forum:
            overwrite.create_threads = False  # type: ignore

        await channel.set_permissions(role, overwrite=overwrite, reason=reason)
        await Messenger(interaction).reply(
            f"""
            **{channel.mention} has been unlocked**
            >>> Manager: {interaction.user.mention}
            For: {role}
            Reason: `{reason or 'No reason provided'}`
            """,
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False),
        )

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @channel_group.command(name="lock-all", description="Lock all channels")  # type: ignore
    async def lock_all(
        self,
        interaction: Interaction,
        role: Optional[Role] = None,
        reason: Optional[str] = None,
    ):
        role = role or interaction.guild.default_role  # type: ignore
        channels = interaction.guild.channels  # type: ignore

        await interaction.response.defer()

        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite.send_messages = False
            overwrite.connect = False

            if channel.type == ChannelType.forum:
                overwrite.create_threads = None  # type: ignore

            await channel.set_permissions(role, overwrite=overwrite, reason=reason)
        await Messenger(interaction).followup_send(
            f"""
            **Locked total `{len(channels)}` channels**
            >>> Manager: {interaction.user.mention}
            For: {role}
            Reason: `{reason or 'No reason provided'}`
            """,
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False),
        )

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @channel_group.command(name="unlock-all", description="Unlock all channels")  # type: ignore
    async def unlock_all(
        self,
        interaction: Interaction,
        role: Optional[Role] = None,
        reason: Optional[str] = None,
    ):
        role = role or interaction.guild.default_role  # type: ignore
        channels = interaction.guild.channels  # type: ignore

        await interaction.response.defer()

        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite.connect = None
            overwrite.send_messages = None

            if channel.type == ChannelType.forum:
                overwrite.create_threads = None  # type: ignore

            await channel.set_permissions(role, overwrite=overwrite, reason=reason)

        await Messenger(interaction).followup_send(
            f"""
            **Unlocked total `{len(channels)}` channels**
            >>> Manager: {interaction.user.mention}
            For: {role}
            Reason: `{reason or 'No reason provided'}`
            """,
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False),
        )

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @channel_group.command(description="Delete channel")  # type: ignore
    async def delete(
        self,
        interaction: Interaction,
        channel: GuildChannel,
        reason: Optional[str] = None,
    ) -> None:
        await channel.delete(reason=reason)
        await Messenger(interaction).reply(
            f"""
            **{channel.mention} has been deleted**
            >>> Manager: {interaction.user.mention}
            Reason: `{reason or 'No reason provided'}`
            """
        )
