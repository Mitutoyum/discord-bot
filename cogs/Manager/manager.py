from .. import Cog

from discord import Member, Role
from discord import app_commands
from discord import Interaction
from core.utils import MessageUtils

from typing import Optional

class Manager(Cog):

    role = app_commands.Group(name='role', description='Role utilities')

    @app_commands.checks.has_permissions(manage_roles=True)
    @role.command()
    async def add(self, interaction: Interaction, user: Member, role: Role, reason: Optional[str] = None):
        await user.add_roles(role, reason=reason)
        await MessageUtils(interaction).reply(content=f'**Added {role.mention} to {user.mention}**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')

    @app_commands.checks.has_permissions(manage_roles=True)
    @role.command()
    async def remove(self, interaction: Interaction, user: Member, role: Role, reason: Optional[str] = None):
        await user.remove_roles(role, reason=reason)
        await MessageUtils(interaction).reply(content=f'**Removed {role.mention} from {user.mention}**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')
    
    @app_commands.checks.has_permissions(manage_roles=True)
    @role.command()
    async def delete(self, interaction: Interaction, role: Role, reason: Optional[str] = None):
        await role.delete(reason=reason)
        await MessageUtils(interaction).reply(content=f'**Deleted {role.name} from the server**\n>>> Manager: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')
