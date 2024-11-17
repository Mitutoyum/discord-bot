from typing import Optional

from discord import app_commands, Interaction, Message, Role, AllowedMentions, TextChannel
from discord.ext.commands import Cog

from core.bot import Bot
from core.utils.cog import CogMixin
from core.utils import config_manager
from core.utils.message import Messenger, ChannelMessenger


def is_enabled(guild_id: str | int) -> bool:
    return config_manager.get_flag(f'guild.{guild_id}.automod.is_enabled', False, check_global=False)

def get_blacklisted_words(guild_id: str | int) -> list[str]:
    return config_manager.get_flag(f'guild.{guild_id}.automod.word_blacklist', [], check_global=False)

def get_blacklisted_roles(guild_id: str | int) -> list[str]:
    return config_manager.get_flag(f'guild.{guild_id}.automod.role_blacklist', [], check_global=False)

def get_automod_channel(bot: Bot, guild_id: str| int) -> TextChannel | None:
    channel_id = config_manager.get_flag(f'guild.{guild_id}.automod.channel', check_global=False)
    return bot.get_channel(channel_id)

def blacklist_word(guild_id: str, word: str) -> None:
    blacklisted_words = get_blacklisted_words(guild_id)
    if word in blacklisted_words:
        return

    blacklisted_words.append(word)
    config_manager.set_flag(f'guild.{guild_id}.automod.word_blacklist', blacklisted_words)

def blacklist_role(guild_id: str, role: Role | str) -> None:
    if isinstance(role, Role):
        role = role.mention

    blacklisted_roles = get_blacklisted_roles(guild_id)

    if role in blacklisted_roles:
        return

    blacklisted_roles.append(role)
    config_manager.set_flag(f'guild.{guild_id}.automod.role_blacklist', blacklisted_roles)


def whitelist_word(guild_id: str, word: str) -> None:
    blacklisted_words = get_blacklisted_words(guild_id)
    if not word in blacklisted_words:
        return

    blacklisted_words.remove(word)
    config_manager.set_flag(f'guild.{guild_id}.automod.word_blacklist', blacklisted_words)

def whitelist_role(guild_id: str, role: Role | str) -> None:
    if isinstance(role, Role):
        role = role.mention

    blacklisted_roles = get_blacklisted_roles(guild_id)

    if not role in blacklisted_roles:
        return

    blacklisted_roles.remove(role)
    config_manager.set_flag(f'guild.{guild_id}.automod.role_blacklist', blacklisted_roles)

class AutoMod(CogMixin):
    
    automod = app_commands.Group(name='automod', description='Auto moderate')

    mention_on_detect = app_commands.Group(name='mention-when-detect', description='Mention role when detect, only works if announce is enabled')

    automod.add_command(mention_on_detect)

    @automod.command(description='Enables automod')
    async def enable(self, interaction: Interaction):
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.is_enabled', True)
        await Messenger(interaction).reply('Automod has been enabled')

    @automod.command(description='Disables automod')
    async def disable(self, interaction: Interaction):
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.is_enabled', False)
        await Messenger(interaction).reply('Automod has been disabled')

    @mention_on_detect.command()
    async def enable(self, interaction: Interaction) -> None:
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.mention_when_detect.is_enabled', True)
        await Messenger(interaction).reply('`mention-when-detect` has been enabled')
    
    @mention_on_detect.command()
    async def disable(self, interaction: Interaction) -> None:
        config_manager.set_flag(f'guild.{interaction.guild.id}.automod.mention_when_detect.is_enabled', False)
        await Messenger(interaction).reply('`mention-when-detect` has been disabled')
    
    @mention_on_detect.command(name='add-role', description='Add the role to mention')
    async def add_role(self, interaction: Interaction, role: Role) -> None:
        messenger = Messenger(interaction)

        roles = config_manager.get_flag(f'guild.{interaction.guild_id}.automod.mention_when_detect.roles', [], check_global=False)
        
        if role in roles:
            return await messenger.reply(f'{role.mention} was already added')

        roles.append(role.mention)
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.mention_when_detect.roles', roles)
        await messenger.reply(f'{role.mention} has been added to the list')
    
    @mention_on_detect.command(name='remove-role', description='Remove the role out of the list, if there is')
    async def remove_role(self, interaction: Interaction, role: Role) -> None:
        messenger = Messenger(interaction)
        roles = config_manager.get_flag(f'guild.{interaction.guild_id}.automod.mention_when_detect.roles', [], check_global=False)

        if not role.mention in roles:
            return await messenger.reply(f'{role.mention} was not added')
        
        roles.remove(role.mention)
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.mention_when_detect.roles', roles)
        await messenger.reply(f'{role.mention} has been removed from the list')
    
    

    @automod.command(name='set-channel', description='Set automod channel')
    async def set_channel(self, interaction: Interaction, channel: Optional[TextChannel] = None) -> None:
        channel = channel or interaction.channel
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.channel', channel.id)

    @automod.command(name='blacklist-word', description='Blacklist a word')
    async def blacklist_word(self, interaction: Interaction, word: str) -> None:
        blacklist_word(interaction.guild_id, word)
        await Messenger(interaction).reply(f'`{word}` has been blacklisted')

    @automod.command(name='blacklist-role', description='Blacklist a role')
    async def blacklist_role(self, interaction: Interaction, role: Role) -> None:
        blacklist_role(interaction.guild_id, role)
        
        await Messenger(interaction).reply(f'{role.mention} has been blacklisted', allowed_mentions=AllowedMentions(roles=False))

    @automod.command(name='whitelist-word', description='Whitelist a word, only works if the word has been blacklisted before')
    async def whitelist_word(self, interaction: Interaction, word: str) -> None:
        whitelist_word(interaction.guild_id, word)
        await Messenger(interaction).reply(f'`{word}` is no longer blacklisted')

    @automod.command(name='whitelist-role', description='whitelist a role, only works if the role has been blacklisted before')
    async def whitelist_role(self, interaction: Interaction, role: Role) -> None:
        whitelist_role(interaction.guild_id, role)
        await Message(interaction).reply(f'{role.mention} is not longer blacklisted', allowed_mentions=AllowedMentions(roles=False))


    @automod.command(name='set-announce', description='Announce to automod channel')
    async def set_announce(self, interaction: Interaction, announce: bool) -> None:
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.announce', announce)
        await Messenger(interaction).reply(f'Announce is now {'enabled' if announce else 'disabled'}')


    # @automod.command(name='mention-on-detect', description='Mention role when detected, only works if annouce is enabled, put none to disable')
    # async def mention_on_detect(self, interaction: Interaction, role: Optional[Role] = None) -> None:
    #     if isinstance(role, Role):
    #         role = role.mention
        
    #     config_manager.set_flag(f'guild.{interaction.guild_id}.automod.mention_role', role)

    #     await Messenger(interaction).reply(f'{role} will now get pinged when someone says the blacklisted words', allowed_mentions=AllowedMentions(roles=False))

    @automod.command(name='delete-on-detect', description='Delete the message contains the word when detected')
    async def delete_on_detect(self, interaction: Interaction, value: bool) -> None:
        config_manager.set_flag(f'guild.{interaction.guild_id}.automod.delete_on_detect', value)
        await Messenger(interaction).reply(f'`delete-on-detect` has been {'enabled' if value else 'disabled'}')
    
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        guild_id = message.guild.id
        automod_channel = get_automod_channel(self.bot, guild_id)

        if not is_enabled(guild_id) or message.author.bot:
            return

        for word in get_blacklisted_words(message.guild.id):
            if word in message.content:
                if config_manager.get_flag(f'guild.{guild_id}.automod.announce', False) and automod_channel:

                    content = f'Blacklisted word detected: `{word}`\n> By: {message.author.mention}\n> Message: {message.jump_url}'
                    pure_content = ''
                    if config_manager.get_flag(f'guild.{guild_id}.automod.mention_when_detect.is_enabled', False, check_global=False):
                        roles = config_manager.get_flag(f'guild.{guild_id}.automod.mention_when_detect.roles', [], check_global=False)

                        for role in roles:
                            pure_content += role 

                    await ChannelMessenger(automod_channel).send(content, pure_content)
                
                if config_manager.get_flag(f'guild.{guild_id}.automod.delete_on_detect', False):
                    await message.delete()
                    
