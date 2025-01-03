import discord

from .modlog import ModLog
from .automod import AutoMod
from datetime import datetime
from typing import Optional
from logging import getLogger

from discord import Interaction, app_commands, Member, User
from discord.ext import tasks

from core.utils.message import Messenger
from core.utils.cog import Cog
from core.utils.transformers import DurationTransformer

logger = getLogger(__name__)

class Moderation(Cog, ModLog, AutoMod, description='A category used for moderating purposes'):

    async def cog_load(self):
        await super().cog_load()
        self.temp_bans.start()
        self.temp_mutes.start()

    @app_commands.describe(
        user = 'The user to ban',
        delete_messages = 'Wether to delete their messages or not',
        duration = 'Duration for the ban, none will be permanent',
        reason = 'The reason for the ban, if any'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Ban member')
    async def ban(self, interaction: Interaction, user: Member | User, delete_messages: Optional[bool] = False, duration: DurationTransformer | None = None, reason: Optional[str] = None):
        messenger = Messenger(interaction)
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
            await messenger.reply(
                f'''
                **{user.mention} has been banned**
                >>> Moderator: {interaction.user.mention}
                Duration: {duration}
                Reason: {reason or 'No reason provided'}
                '''
            )
        else:
            await messenger.reply(f'{user.mention} was already banned')

    @app_commands.describe(
        user = 'The user to unban',
        reason = 'The reason for the unban, if any'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Unban user')
    async def unban(self, interaction: Interaction, user: User, reason: Optional[str] = None) -> None:
        await interaction.guild.unban(user, reason=reason)
        async with self.bot.connection_pool.acquire() as db:
            async with db.execute('SELECT EXISTS(SELECT * FROM temp_bans WHERE userid=? AND guild_id=?)', (user.id, interaction.guild_id)) as cursor:
                (result) = await cursor.fetchone()
                if result:
                    await db.execute('DELETE FROM temp_bans WHERE userid=? AND guild_id=?', (user.id, interaction.guild_id))
                    await db.commit()

        await Messenger(interaction).reply(
            f'''
            **{user.mention} has been unbanned**
            >>> Moderator: {interaction.user.mention}
            Reason: {reason or 'No reason provided'}'
            '''
        )

    @app_commands.describe(
        member = 'The member to kick',
        reason = 'The reason for the kick, if any'
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Kick member')
    async def kick(self, interaction: Interaction, member: Member, reason: Optional[str] = None) -> None:
        await member.kick(reason=reason)
        await Messenger(interaction).reply(
            f'''
            **{member.mention} has been kicked**
            >>> Moderator: {interaction.user.mention}
            Reason: {reason or 'No reason provided'}
            '''
        )
    

    @app_commands.describe(
        member = 'The member to mute',
        duration = 'Duration for the mute, none will be permanent',
        reason = 'The reason for the mute, if any'
    )
    @app_commands.checks.has_permissions(mute_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Mute member')
    async def mute(self, interaction: Interaction, member: Member, duration: Optional[DurationTransformer] = None, reason: Optional[str] = None):
        muted_role = discord.utils.get(interaction.guild.roles, name='Muted')
        if not muted_role:
            return await Messenger(interaction).reply(f'The server does not have `Muted` role, run {await self.bot.tree.get_mention('setup-muted-role')} to create one')

        if discord.utils.get(member.roles, id=muted_role.id):
            return await Messenger(interaction).reply(f'{member.mention} was already muted')

        await member.add_roles(muted_role, reason=reason)

        if duration:
            duration = datetime.now() + duration
            async with self.bot.connection_pool.acquire() as connection:
                await connection.execute('INSERT INTO temp_mutes(userid, guild_id, release_date) VALUES(?, ?, ?)', (member.id, interaction.guild_id, duration.isoformat()))
                await connection.commit()
            duration = discord.utils.format_dt(duration, style='R')
        else:
            duration = '`Permanent`'
        await Messenger(interaction).reply(
            f'''
            **{member.mention} has been muted**
            >>> Moderator: {interaction.user.mention}
            Duration: {duration}
            Reason: {reason or 'No reason provided'}
            '''
        )

    @app_commands.describe(
        member = 'The member to unmute',
        reason = 'The reason for the unmute, if any'
    )
    @app_commands.checks.has_permissions(mute_members=True)
    @app_commands.guild_only()
    @app_commands.command(description='Unmute member')
    async def unmute(self, interaction: Interaction, member: Member, reason: Optional[str] = None):
        muted_role = discord.utils.get(interaction.guild.roles, name='Muted')
        if not discord.utils.get(member.roles, id=muted_role.id):
            return await Messenger(interaction).reply(f'{member.mention} is not muted')
        
        await member.remove_roles(muted_role, reason=reason)

        async with self.bot.connection_pool.acquire() as connection:
            async with connection.execute('SELECT EXISTS(SELECT * FROM temp_mutes WHERE userid=? AND guild_id=?)', (member.id, interaction.guild_id)) as cursor:
                (result) = await cursor.fetchone()
                if result:
                    await connection.execute('DELETE FROM temp_mutes WHERE userid=? AND guild_id=?', (member.id, interaction.guild_id))
                    await connection.commit()

        await Messenger(interaction).reply(
            f'''
            **{member.mention} has been unmuted**
            >>> Moderator: {interaction.user.mention}
            Reason: {reason or 'No reason provided'}
            '''
        )
        
    @app_commands.describe(
        member = 'The member to timeout',
        until = 'The amount of time the member should be timed out for',
        reason = 'The reason for the timeout, if any'
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.guild_only()
    @app_commands.command(description=f'Timeout member, if you wan\'t a permanent mute consider using mute command instead')
    async def timeout(self, interaction: Interaction, member: Member, until: DurationTransformer, reason: Optional[str] = None):
        await member.timeout(until, reason=reason)
        await Messenger(interaction).reply(
            f'''
            **{member.mention} has been timeout**
            >>> Moderator: {interaction.user.mention}
            Until: {discord.utils.format_dt(datetime.now() + until, 'R')}
            Reason: {reason or 'No reason provided'}
            '''
        )


    @app_commands.checks.has_permissions(manage_roles=True, manage_channels=True)
    @app_commands.guild_only()
    @app_commands.command(name='setup-muted-role', description='Setup a Muted role for the server')
    async def setup_muted_role(self, interaction: Interaction):
        guild = interaction.guild
        muted_role = discord.utils.get(guild.roles, name='Muted')

        if not muted_role:
            muted_role = await interaction.guild.create_role(name='Muted')
        
        for channel in guild.channels:
            overwrite = channel.overwrites_for(muted_role)
            overwrite.send_messages = False
            overwrite.add_reactions = False
            await channel.set_permissions(muted_role, overwrite=overwrite, reason='Muted role setup')

        await Messenger(interaction).reply(
            f'''
            **{muted_role} has been created**
            >>> Author: {interaction.user.mention}
            '''
        )
            



    @tasks.loop(seconds=1)
    async def temp_bans(self):
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
                    
    @tasks.loop(seconds=1)
    async def temp_mutes(self):
        now = datetime.now()
        async with self.bot.connection_pool.acquire() as db:
            async with db.execute('SELECT rowid, * FROM temp_mutes') as cursor:
                async for record in cursor:
                    (rowid, userid, guild_id, release_date) = record
                    try:
                        if datetime.fromisoformat(release_date) <= now:
                            user = self.bot.get_guild(guild_id).get_member(userid)
                            await user.remove_roles(discord.utils.get(user.roles, name='Muted'))
                            await db.execute(f'DELETE FROM temp_mutes WHERE rowid={rowid}')
                            await db.commit()
                    
                    except AttributeError:
                        await db.execute('DELETE FROM temp_mutes WHERE rowid=?', tuple(rowid))

    @temp_bans.before_loop
    async def tb_before_loop(self):
        await self.bot.wait_until_ready()

    @temp_mutes.before_loop
    async def tm_before_loop(self):
        await self.bot.wait_until_ready()