import discord

from .. import Cog
from datetime import datetime
from typing import Optional
from logging import getLogger
from discord import Interaction
from discord import app_commands
from discord.ext import tasks
from core.utils.helpers import MessageUtils
from core.utils import transformers



logger = getLogger(__name__)


class Moderation(Cog):

    async def cog_load(self):
        await super().cog_load()
        self.tempban_check.start()

    @app_commands.describe(
        user = 'The user to ban',
        delete_messages = 'Wether to delete their messages or not',
        duration = 'Duration for the ban, none will be permanent',
        reason = 'The reason for banning, if any'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Ban user')
    async def ban(self, interaction: Interaction, user: discord.Member | discord.User, delete_messages: Optional[bool] = False, duration: transformers.DurationConverter | None = None, reason: Optional[str] = None):
        message_utils = MessageUtils(interaction)
        guild = interaction.guild
        try:
            await guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.guild.ban(
                user,
                reason = reason,
                delete_message_days = 7 if delete_messages else 0
            )
            if duration:
                    duration = datetime.now() + duration
                    async with self.bot.connection_pool.acquire() as db:
                        await db.execute(f'INSERT INTO temp_bans(userid, guild_id, release_date) VALUES(?, ?, ?)', (user.id, interaction.guild_id, duration.isoformat()))
                        await db.commit()
                    duration = discord.utils.format_dt(duration, 'R')
            else:
                duration = '`Permanent`'
            await message_utils.reply(content=f'**{user.mention} has been banned**\n>>> Moderator: {interaction.user.mention}\nDuration: {duration}\nReason: {reason or 'No reason provided'}')
        else:
            await message_utils.reply(content=f'{user.mention} was already banned')

    @app_commands.describe(
        user = 'The user to unban',
        reason = 'The reason for unbanning, if any'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Unban user')
    async def unban(self, interaction: Interaction, user: discord.User, reason: Optional[str] = None) -> None:
        message_utils = MessageUtils(interaction)
        await interaction.guild.unban(user, reason=reason)
        async with self.bot.connection_pool.acquire() as db:
            async with db.execute('SELECT EXISTS(SELECT * FROM temp_bans WHERE userid=? AND guild_id=?)', (user.id, interaction.guild_id)) as cursor:
                (result) = await cursor.fetchone()
                if result:
                    await db.execute('DELETE FROM temp_bans WHERE userid=? AND guild_id=?', (user.id, interaction.guild_id))
                    await db.commit()

        await message_utils.reply(content=f'**{user.mention} has been unbanned**\n>>> Moderator: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')

    
    @app_commands.describe(
        user = 'The user to kick',
        reason = 'The reason for kicking, if any'
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Kick user')
    async def kick(self, interaction: Interaction, user: discord.Member, reason: Optional[str] = None) -> None:
        await user.kick(reason=reason)
        await MessageUtils(interaction).reply(content=f'**{user.mention} has been kicked**\n>>> Moderator: {interaction.user.mention}\nReason: {reason or 'No reason provided'}')
    
    @tasks.loop(seconds=1)
    async def tempban_check(self):
        now = datetime.now()
        async with self.bot.connection_pool.acquire() as db:
            async with db.execute('SELECT rowid, * FROM temp_bans') as cursor:
                async for record in cursor:
                    (rowid, userid, guild_id, release_date) = record
                    try:
                        if datetime.fromisoformat(release_date) <= now:
                            await self.bot.get_guild(guild_id).unban(discord.Object(userid))
                            await db.execute(f'DELETE FROM temp_bans WHERE rowid={rowid}')
                            await db.commit()
                    except discord.NotFound: # User no longer exists or banned
                        await db.execute('DELETE FROM temp_bans WHERE userid=?', tuple(userid))
                    except AttributeError: # Bot no longer exists in the server
                        await db.execute('DELETE FROM temp_bans WHERE guild_id=?', tuple(guild_id))
                    



    @tempban_check.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()