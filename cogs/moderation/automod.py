from typing import Optional

from discord import (
    app_commands,
    Interaction,
    Message,
    Role,
    AllowedMentions,
    TextChannel,
)
from discord.ext.commands import Cog

from core.bot import Bot
from core.utils.cog import CogMixin
from core.utils import config_manager
from core.utils.message import Messenger, ChannelMessenger


def get_toggle(guild_id: str | int) -> bool:
    return config_manager.get_flag(
        f"guild.{guild_id}.automod.toggle", False, check_global=False
    )  # type: ignore


def get_blacklisted_words(guild_id: str | int) -> list[str]:
    return config_manager.get_flag(
        f"guild.{guild_id}.automod.word_blacklist", [], check_global=False
    )  # type: ignore


def get_automod_channel(bot: Bot, guild_id: str | int) -> TextChannel | None:
    channel_id = config_manager.get_flag(
        f"guild.{guild_id}.automod.channel", check_global=False
    )
    return bot.get_channel(channel_id)  # type: ignore


def blacklist_word(guild_id: str, word: str) -> None:
    blacklisted_words = get_blacklisted_words(guild_id)
    if word in blacklisted_words:
        return

    blacklisted_words.append(word)
    config_manager.set_flag(
        f"guild.{guild_id}.automod.word_blacklist", blacklisted_words
    )


def unblacklist_word(guild_id: str, word: str) -> None:
    blacklisted_words = get_blacklisted_words(guild_id)
    if word not in blacklisted_words:
        return

    blacklisted_words.remove(word)
    config_manager.set_flag(
        f"guild.{guild_id}.automod.word_blacklist", blacklisted_words
    )


class AutoMod(CogMixin):
    automod = app_commands.Group(name="automod", description="Automically moderate")

    @automod.command(description="Enable automod")  # type: ignore
    async def enable(self, interaction: Interaction):
        config_manager.set_flag(f"guild.{interaction.guild_id}.automod.toggle", True)
        await Messenger(interaction).reply("Automod has been enabled")

    @automod.command(description="Disable automod")  # type: ignore
    async def disable(self, interaction: Interaction):
        config_manager.set_flag(f"guild.{interaction.guild_id}.automod.toggle", False)
        await Messenger(interaction).reply("Automod has been disabled")

    @automod.command(name="set-channel", description="Set automod channel")  # type: ignore
    async def set_channel(
        self, interaction: Interaction, channel: Optional[TextChannel] = None
    ):  # type: ignore
        channel: TextChannel = channel or interaction.channel  # type: ignore
        config_manager.set_flag(
            f"guild.{interaction.guild_id}.automod.channel", channel.id
        )
        await Messenger(interaction).reply(
            f"automod channel has been set to {channel.mention}"
        )

    @automod.command(name="blacklist-word", description="Blacklist a word")  # type: ignore
    async def blacklist_word(self, interaction: Interaction, word: str):
        blacklist_word(interaction.guild_id, word)  # type: ignore
        await Messenger(interaction).reply(f"`{word}` has been blacklisted")

    @automod.command(name="unblacklist-word", description="Unblacklist word")  # type: ignore
    async def unblacklist_word(self, interaction: Interaction, word: str):
        unblacklist_word(interaction.guild_id, word)  # type: ignore
        await Messenger(interaction).reply(f"`{word}` is no longer blacklisted")

    @automod.command(name="auto-announce", description="Announce to automod channel")  # type: ignore
    async def auto_announce(
        self, interaction: Interaction, toggle: bool, alert: Optional[bool] = False
    ):
        path = f"guild.{interaction.guild_id}.automod.auto_announce"
        config_manager.set_flag(f"{path}.toggle", toggle)
        config_manager.set_flag(f"{path}.alert", alert)
        await Messenger(interaction).reply(
            f'`auto-announce` is now {'enabled' if toggle else 'disabled'}'
        )

    @automod.command(
        name="auto-delete",
        description="Delete the message contains the word when detected",
    )  # type: ignore
    async def auto_delete(self, interaction: Interaction, toggle: bool):
        config_manager.set_flag(
            f"guild.{interaction.guild_id}.automod.auto_delete", toggle
        )
        await Messenger(interaction).reply(
            f'`auto_delete` has been {'enabled' if toggle else 'disabled'}'
        )

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        guild_id = message.guild.id  # type: ignore
        automod_channel = get_automod_channel(self.bot, guild_id)

        if not get_toggle(guild_id) or message.author.bot:
            return

        for word in get_blacklisted_words(message.guild.id):  # type: ignore
            if word in message.content:
                if (
                    config_manager.get_flag(
                        f"guild.{guild_id}.automod.auto_announce",
                        False,
                        check_global=False,
                    )
                    and automod_channel
                ):
                    content = f"""
                    Blacklisted word detected: **`{word}`**
                    >>> By: {message.author.mention}
                    Message: {message.jump_url}
                    """
                    pure_content = config_manager.get_flag(
                        f"guild.{guild_id}.automod.auto_announce.alert",
                        False,
                        check_global=False,
                    )
                    if pure_content:
                        pure_content = "@here"

                    await ChannelMessenger(automod_channel).send(content, pure_content)

                if config_manager.get_flag(
                    f"guild.{guild_id}.automod.auto_delete", False, check_global=False
                ):
                    await message.delete()
