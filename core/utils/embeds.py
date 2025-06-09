from datetime import datetime
from typing import Optional

import discord
from discord import Embed

from core.utils import config_manager


class BaseEmbed(Embed):
    def __init__(
        self,
        # author: Optional[discord.User | discord.Member] = None,
        guild_id: Optional[int] = None,
        **kwargs,
        # colour=None,
        # color=None,
        # title=None,
        # type="rich",
        # url=None,
        # description=None,
        # timestamp=None,
    ):
        color = config_manager.get_flag(
            f"guild.{guild_id}.color" if guild_id else "global.color"
        )

        kwargs["color"] = color
        kwargs["colour"] = color

        super().__init__(**kwargs)
        # timestamp = datetime.now()
        # super().__init__(
        #     colour=colour,
        #     color=color,
        #     title=title,
        #     type=type,
        #     url=url,
        #     description=description,
        #     timestamp=timestamp
        # )

        # if author:
        #     self.set_footer(
        #         text=f"Requested by {author.name}", icon_url=author.display_avatar.url
        #     )
