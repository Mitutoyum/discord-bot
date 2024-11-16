import discord
import json

from typing import Literal, Any, Callable, Literal
from inspect import signature

from discord import Interaction, app_commands
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
            clone.pop(i)
            break
        clone = clone[i]
    
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(bot_config, file, indent=4)