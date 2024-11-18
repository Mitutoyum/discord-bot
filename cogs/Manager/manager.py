from typing import Optional

from discord import Member, Role, AllowedMentions
from discord.abc import GuildChannel
from discord import app_commands
from discord import Interaction

from core.utils.message import Messenger
from core.utils.cog import Cog

from .channel import Channel
from .role import Role

class Manager(Cog, Role, Channel):
    pass