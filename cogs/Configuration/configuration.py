from .. import Cog
from typing import Literal

from discord import app_commands, Interaction
from discord.ext import commands

from core import errors
from core.utils import helpers, embeds, config_manager
from core.utils.message import Messenger

class Configuration(Cog, description='A category specifically for bot\'s configuration'):
    
    config_group = app_commands.Group(
        name = 'config',
        description='A group with loads of command to modify the bot\'s behavior'
    )
    set_flag = app_commands.Group(
        name = 'set',
        description = 'A subgroup contains all of the flags that you can set' # todo
    )
    config_group.add_command(set_flag)



    for flag, metadata in config_manager.flags.items(): # i know this is cursed
        async def command(self, interaction: Interaction, scope, **kwargs):
            flag_name = interaction.command.name
            flag = config_manager.flags[flag_name]

            if scope == 'local':
                if not interaction.guild:
                    raise errors.GuildOnly('Local scope can only be used in guilds')
                if not helpers.is_server_owner(interaction):
                    raise errors.NotServerOwner
            elif scope == 'global' and not await self.bot.is_owner(interaction.user):
                raise commands.NotOwner
            
            if flag.get('callback'):
                await flag['callback'](interaction, **kwargs)

            path = f'servers.{interaction.guild_id}.{flag_name}' if scope == 'local' else f'global.{flag_name}'
            kwargs = kwargs.get('value') or kwargs.get(flag_name) or kwargs

            config_manager.set_flag(path, kwargs)
            await Messenger(interaction).reply(content=f'```Successfully changed {flag_name}```')
        
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

        command.__code__ = command.__code__.replace(co_name=flag, co_argcount=argcount, co_flags=131, co_varnames=tuple(params), co_nlocals=len(params))
        command.__annotations__['scope'] = Literal['global', 'local'] if metadata.get('scope') == 'hybrid' else Literal[metadata.get('scope')]
        set_flag.command(name=flag, description=metadata['description'])(command)
        command.__code__ = old_code

    
    @app_commands.choices(
        flag = [
            app_commands.Choice(name=i, value=i)
            for i in config_manager.flags
        ]
    )
    @config_group.command(name='get', description='Get information about a flag')
    async def get_flag(self, interaction: Interaction, flag: app_commands.Choice[str]):
        metadata = config_manager.flags[flag.name]

        if (scope := metadata['scope']) == 'hybrid':
            scope = ['global', 'local']
        else:
            scope = list(scope)

        embed = embeds.BaseEmbed(interaction.user)
        embed.title = f'Showing flag: `{flag.name}`'
        embed.description = f'```{metadata.get('description')}```'
        embed.add_field(
            name = '> Allowed scopes',
            value = f'{' '.join([f'`{i}`'for i in scope])}'
        )
        embed.add_field(
            name = '> Current values',
            value = '\n'.join([
                f'`{i}`: {config_manager.get_flag(f'servers.{interaction.guild.id}.{flag.name}' if i == 'local' else f'global.{flag.name}', 'Not set', check_global=False, add_if_not_exist=False)}' for i in scope]), inline=False
            )
        
        await Messenger(interaction, use_embed_check=False).reply(embed=embed)