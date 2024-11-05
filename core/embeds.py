import discord

from discord import Embed
from core import config
from datetime import datetime

class BaseEmbed(Embed):
    def __init__(self, author: discord.User, *, colour = None, color = None, title = None, type = 'rich', url = None, description = None, timestamp = None):
        super().__init__(colour=colour, color=config.get_flag('global.default_color'), title=title, type=type, url=url, description=description, timestamp=timestamp)
        self.set_footer(text=f'Requested by {author.name}', icon_url=author.display_avatar.url)
        self.timestamp = datetime.today()