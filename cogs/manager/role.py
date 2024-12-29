from typing import Optional

from discord import app_commands, Role, Member, Interaction  # type: ignore

from core.utils.cog import CogMixin
from core.utils.message import Messenger


class Role(CogMixin):
    role_group = app_commands.Group(name="role", description="Role management")

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role_group.command()  # type: ignore
    async def add(
        self,
        interaction: Interaction,
        user: Member,
        role: Role,
        reason: Optional[str] = None,
    ):
        await user.add_roles(role, reason=reason)  # type: ignore
        await Messenger(interaction).reply(  # type: ignore
            f"""
            **Added {role.mention} to {user.mention}**\n
            >>> Manager: {interaction.user.mention}\n
            Reason: `{reason or 'No reason provided'}`
            """
        )

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role_group.command()  # type: ignore
    async def remove(
        self,
        interaction: Interaction,
        user: Member,
        role: Role,
        reason: Optional[str] = None,
    ):
        await user.remove_roles(role, reason=reason)  # type: ignore
        await Messenger(interaction).reply(
            f"""
            **Removed {role.mention} from {user.mention}**\n
            >>> Manager: {interaction.user.mention}\n
            Reason: `{reason or 'No reason provided'}`
            """
        )

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @role_group.command()  # type: ignore
    async def delete(
        self, interaction: Interaction, role: Role, reason: Optional[str] = None
    ):
        await role.delete(reason=reason)  # type: ignore
        await Messenger(interaction).reply(
            f"""
            **Deleted `{role.name}` from the server**\n
            >>> Manager: {interaction.user.mention}\n
            Reason: `{reason or 'No reason provided'}`
            """
        )
