from core.utils.cog import Cog

from .channel import Channel
from .role import Role


class Manager(Cog, Role, Channel):
    pass

