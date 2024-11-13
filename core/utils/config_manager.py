import discord
import json

from typing import Literal, Any, Callable, Literal
from discord import Interaction
from core.config import config_path

def get_config() -> dict:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    return config

def get_flag(path: str, default: Any = None, *, check_global: bool = True, add_if_not_exist: bool = True):
    path_list  = path.split('.')
    config = get_config()
    for i in path_list:
        try:
            config = config[i]
        except KeyError:
            if check_global and path_list[0] != 'global':
                return get_flag(
                    '.'.join([*(['global'] + path_list[2:])]),
                    default,
                    check_global=False,
                    add_if_not_exist=add_if_not_exist
                )
            if add_if_not_exist:
                set_flag(path, default)
            return default
    
    return config


def set_flag(path: str, value):
    path = path.split('.')
    bot_config = get_config()
    clone = bot_config

    for i in path:
        if i == path[-1]:
            clone[i] = value
        else:
            clone = clone.setdefault(i, {})

    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(bot_config, file, indent=4)

def delete_flag(path: str):
    path = path.split('.')
    bot_config = get_config()
    clone = bot_config

    for i in path:
        if i == path[-1]:
            del clone[i]
            break
        clone = clone[i]
    
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(bot_config, file)

def add_flag(flag: str, value: dict | Any, *, scope: Literal['global', 'local', 'hybrid'] = 'hybrid', description: str | None = '...', choices = None):
    flags[flag] = {
        'scope': scope,
        'choices': choices,
        'description': description,
        'value': value
    }
    def decorator(func: Callable):
        flags[flag]['callback'] = func

    return decorator


flags = {}

add_flag('prefix', '!', description='The prefix for the bot to use')
add_flag('default_color', 5793266, description='The color for the bot to use (mainly for embeds)')
add_flag('use_embed', False, description='Wether if the bot should use embed when sending message or not')
add_flag('mention_prefix', False, description='Use the bot\'s mention as the prefix, this does not override the current prefix')

@add_flag('activity', {
    'type': {'annotation': Literal['playing', 'listening', 'competing', 'streaming', 'watching', 'unknown', 'custom']},
    'name': {'annotation': str | None},
    'url': {'annotation': str | None},
    'state': {'annotation': str | None},
    'details': {'annotation': str | None},
    'platform': {'annotation': str | None},
    'application_id': {'annotation': int | None}
}, scope='global')
async def set_activity(inter: Interaction, **kwargs):
    activity = discord.ActivityType[kwargs['type']]
    kwargs.pop('type')
    await inter.client.change_presence(activity=discord.Activity(type=activity, **kwargs))

@add_flag('status', {
    'value': {
        'annotation': Literal['online', 'offline', 'dnd', 'idle']
    }
}, scope='global', description='Set bot\'s status')
async def set_status(inter: Interaction, **kwargs):
    status = discord.Status[kwargs['value']]
    await inter.client.change_presence(status=status)