from typing import Optional

from discord.ext.commands import Context
from discord import Interaction, Message, TextChannel
from core.utils import config_manager, embeds


class Messenger():
    def __init__(self, cls: Context | Interaction, use_embed_check: Optional[bool] = True):
        assert isinstance(cls, (Context, Interaction))

        self.cls = cls
        self.use_embed = False

        if use_embed_check:
            path = f'guild.{cls.guild.id}.use_embed' if cls.guild else 'global.use_embed'
            self.use_embed = config_manager.get_flag(path, self.use_embed)

    async def reply(self, *args, **kwargs) -> Message  | None:
        cls = self.cls
        content = None

        if args:
            content = args[0]
        else:
            content = kwargs.get('content')

        author = getattr(cls, 'user', None) or cls.author
        send_func = getattr(cls, 'reply', None) or cls.response.send_message
        

        if self.use_embed and content:
            embed = embeds.BaseEmbed(author, cls.guild.id, description=content)
            kwargs.pop('content', None)

            if kwargs.get('embed'):
                kwargs['embeds'] = [embed, kwargs['embed']]
            elif kwargs.get('embeds'):
                kwargs['embeds'].append(embed)
            else:
                kwargs['embed'] = embed

            return await send_func(**kwargs)

        return await send_func(*args, **kwargs)
    
    async def edit(self, message: Message, **kwargs):
        if self.use_embed and 'content' in kwargs:
            embed = embeds.BaseEmbed(description=kwargs.get('content'))
            kwargs.pop('content')
            return await message.edit(embed=embed, **kwargs)
        return await message.edit(**kwargs)
    
class ChannelMessenger:
    def __init__(self, channel: TextChannel, use_embed_check: bool = True):
        self.channel = channel
        self.use_embed_check = False

        if use_embed_check:
            path = f'guild.{channel.guild.id}.use_embed'
            self.use_embed = config_manager.get_flag(path, self.use_embed_check)
        
    async def send(self, *args, **kwargs):
        channel = self.channel
        content = None
        pure_content = None

        if args:
            content = args[0]
            try:
                pure_content = args[1]
            except IndexError:
                pass
        else:
            content = kwargs.get('content')
            pure_content = kwargs.get('pure_content')
        

        if self.use_embed and content:
            embed = embeds.BaseEmbed(guild_id=channel.guild.id, description=content)
            if pure_content:
                kwargs['content'] = pure_content
            else:
                kwargs.pop('content', None)

            if kwargs.get('embed'):
                kwargs['embeds'] = [embed, kwargs['embed']]
            elif kwargs.get('embeds'):
                kwargs['embeds'].append(embed)
            else:
                kwargs['embed'] = embed

            return await channel.send(**kwargs)

        return await channel.send(*args, **kwargs)

