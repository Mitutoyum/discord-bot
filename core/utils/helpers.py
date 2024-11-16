import discord
import typing

from collections import abc
from logging import getLogger
from inspect import signature

from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction, Message

from core import errors

from . import views, embeds, config_manager
from .message import Messenger

logger = getLogger(__name__)

async def error_handler(cls: Context | Interaction, exception: commands.CommandError | app_commands.AppCommandError | errors.BotException | Exception) -> bool:
    if isinstance(exception, (commands.CommandInvokeError, app_commands.CommandInvokeError)):
        exception = exception.__cause__

    if exception.args:
        await Messenger(cls).reply(content=exception.args[0])
        return True
    return False
    

    
async def get_prefix(bot: commands.Bot, message: Message) -> str | abc.Iterable[str]:
    mention_prefix = config_manager.get_flag('global.mention_prefix' if not message.guild else f'servers.{message.guild.id}.mention_prefix', False)
    prefix = config_manager.get_flag('global.prefix' if not message.guild else f'servers.{message.guild.id}.prefix')
    return commands.when_mentioned_or(prefix)(bot, message) if mention_prefix and prefix else prefix or commands.when_mentioned(bot, message)
    

def get_params(callback: abc.Callable) -> dict[str, dict]:
    flags = {}
    for name, parameter in signature(callback).parameters.items():
        if name == 'self': continue
        elif parameter.annotation in (discord.Interaction, commands.Context): continue

        if type(parameter.annotation) is commands.flags.FlagsMeta:
            for name, flag in parameter.annotation.get_flags().items():
                flags[name] = {
                    'description': flag.description,
                    'annotation': flag.annotation,
                    'default': flag.default,
                    'aliases': flag.aliases
                }
        elif parameter.default in (commands.Parameter, app_commands.Parameter):
            flags[name] = {
                'description': parameter.default.description,
                'annotation': parameter.default.annotation,
                'default': parameter.default.default,
            }
        else:
            flags[name] = {
                'annotation': parameter.annotation,
                'default': parameter.default
            }

    return flags

def get_user_count(bot: commands.Bot) -> int:
    user_count = 0

    for guild in bot.guilds:
        user_count += guild.member_count or 0

    return user_count


def is_typing_optional(annotation) -> bool:
    return (typing.get_origin(annotation) is typing.Union and type(None) in typing.get_args(annotation)) or False


async def confirm_prompt(cls: Context | Interaction, use_embed_check: bool = True, timeout: float = float('inf')):
    author = getattr(cls, 'author', None) or getattr(cls, 'user', None)
    view = views.ConfirmPrompt(author, timeout=timeout)
    message = await Messenger(cls, use_embed_check).reply(content='Do you want to proceed?', view=view)
    view.message = message

    if await view.wait() != False or not view.value:
        raise
    return message

def is_server_owner(cls: Context | Interaction):
    assert isinstance(cls, (Context, Interaction))
    author = getattr(cls, 'author', None) or cls.user

    return author == cls.guild.owner