import discord

from .. import Cog

from core import utils, embeds, config, errors, views
from typing import Literal
from core.utils import MessageUtils
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

class Admin(Cog):
    config_group = app_commands.Group(name='config', description='A set of commands to configure the bot')
    set_flag = app_commands.Group(name='set', description='Set')
    config_group.add_command(set_flag)

    for flag, metadata in config.flags.items():
        async def command(self, inter: Interaction, scope, **kwargs):
            flags = config.flags
            flag_name = inter.command.name
            flag = flags[flag_name]

            if scope == 'local':
                if not inter.guild:
                    raise errors.GuildOnly('Local scope can only be used in guilds')
                if not utils.is_server_owner(inter):
                    raise errors.NotServerOwner
            elif scope == 'global' and not await self.bot.is_owner(inter.user):
                raise commands.NotOwner
            
            if flag.get('callback'):
                await flag['callback'](inter, **kwargs)
            path = f'servers.{inter.guild_id}.{flag_name}' if scope == 'local' else f'global.{flag_name}'
            kwargs = kwargs.get('value') or kwargs.get(flag_name) or kwargs
            # config.set_flag(path, (kwargs['value'] or kwargs['value']) if not isinstance(flag['value'], dict) else kwargs)
            config.set_flag(path, kwargs)
            await MessageUtils(inter).reply(content=f'```Successfully changed {flag_name}```')
        
        old_code = command.__code__
        
        params = list(old_code.co_varnames)
        params.remove('kwargs')
        argcount = len(params[:command.__code__.co_argcount])
        if isinstance(metadata['value'], dict):
            for k, v in metadata['value'].items():
                params.insert(argcount, k)
                command.__annotations__[k] = v['annotation']
                if v.get('default'):
                    command.__defaults__ = (command.__defaults__ or ()) + (v['default'],)
                if v.get('description'):
                    app_commands.describe(**{k: v['description']})(command)
                argcount += 1
        else:
            params.insert(argcount, 'value')
            command.__annotations__['value'] = type(metadata['value'])
            command.__defaults__ = (command.__defaults__ or ()) + (metadata['value'],)
            argcount += 1

        command.__code__ = command.__code__.replace(co_argcount=argcount, co_flags=131, co_varnames=tuple(params), co_nlocals=len(params))
        command.__annotations__['scope'] = Literal['global', 'local'] if metadata.get('scope') == 'hybrid' else Literal[metadata.get('scope')]
        set_flag.command(name=flag, description=metadata['description'])(command)
        command.__code__ = old_code


    @app_commands.choices(
        flag = [
            app_commands.Choice(name=i, value=i)
            for i in config.flags
        ]
    )
    @config_group.command(name='get', description='Get information about a flag')
    async def get_flag(self, inter: Interaction, flag: app_commands.Choice[str]):
        metadata = config.flags[flag.name]
        if (scope := metadata['scope']) == 'hybrid':
            scope = ['global', 'local']
        else:
            scope = list(scope)
        embed = embeds.BaseEmbed(inter.user)
        embed.title = f'Showing flag: `{flag.name}`'
        embed.description = f'```{metadata.get('description')}```'
        embed.add_field(
            name = '> Allowed scopes',
            value = f'{' '.join([f'`{i}`'for i in scope])}'
        )
        embed.add_field(
            name = '> Current values',
            value = '\n'.join([
                f'`{i}`: {config.get_flag(f'servers.{inter.guild.id}.{flag.name}' if i == 'local' else f'global.{flag.name}', 'Not set', check_global=False, add_if_not_exist=False)}' for i in scope]), inline=False)
        await MessageUtils(inter, use_embed_check=False).reply(embed=embed)
    
    @commands.is_owner()
    @commands.command(description='Clears all application commands from the tree')
    async def clear_commands(self, ctx: Context, guild_id: int | None = None) -> None:
        guild = discord.Object(guild_id) if guild_id else None
        self.bot.tree.clear_commands(guild=guild)
        await MessageUtils(ctx).reply(content='Successfully cleared all application commands')

    @commands.is_owner()
    @commands.command(description='Sync slash commands, You should only use this when a slash command changes, DO NOT spam it')
    async def sync(self, ctx: Context, guild_id: int | None = None) -> None:
        synced_cmds = await self.bot.tree.sync(guild=guild_id)
        self.bot.tree.copy_global_to
        await MessageUtils(ctx).reply(content=f'Synced {len(synced_cmds)} command(s)')