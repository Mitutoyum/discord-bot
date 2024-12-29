import inspect
from typing import Literal, Optional


import discord
from discord.ext import commands
from discord import app_commands, Interaction

from core import errors
from core.utils.cog import Cog
from core.utils import config_manager, helpers
from core.utils.message import Messenger


def transform(
    scope: Literal["local", "global", "hybrid"] = "hybrid",
    *,
    permission_check: bool = True,
    auto_respond: bool = True,
):
    def decorator(cls: app_commands.Command):
        old_callback = cls._callback

        async def callback(self, interaction: Interaction, **kwargs):
            scope = kwargs["scope"]
            kwargs.pop("scope")

            if scope == "local":
                if not interaction.guild:
                    raise errors.GuildOnly("Local scope can only be used in guilds")
                if not helpers.is_server_owner(interaction):
                    raise errors.NotServerOwner(
                        "You are not permitted to use this command"
                    )
            else:
                if not await self.bot.is_owner(interaction.user):
                    raise commands.NotOwner("You are not permitted to use this command")

            old_kwargs = kwargs.copy()

            for k, v in old_kwargs.items():
                if v == app_commands.Choice:
                    old_kwargs[k] = v.value

            path = (
                f"global.{cls.name}"
                if scope == "global"
                else f"guild.{interaction.guild_id}.{cls.name}"
            )
            config_manager.set_flag(
                path,
                list(old_kwargs.values())[0] if len(old_kwargs) == 1 else old_kwargs,
            )
            await old_callback(self, interaction, **kwargs)
            if auto_respond:
                await Messenger(interaction).reply(
                    f"`{old_callback.__name__}` has been changed"
                )

        annotation = Literal["global", "local"] if scope == "hybrid" else Literal[scope]
        cls._params = {
            "scope": app_commands.transformers.annotation_to_parameter(
                annotation,
                inspect.Parameter(
                    "scope",
                    inspect._ParameterKind.POSITIONAL_OR_KEYWORD,
                    annotation=annotation,
                ),
            )
        } | cls._params
        cls._callback = callback

        return cls

    return decorator


class Configuration(Cog):
    config_group = app_commands.Group(
        name="config",
        description="A group with loads of command to modify the bot's behavior",
    )
    set_flag = app_commands.Group(
        name="set", description="A subgroup contains all of the flags that you can set"
    )
    config_group.add_command(set_flag)

    @transform()
    @set_flag.command()
    async def use_embed(self, interaction: Interaction, value: bool) -> None:
        pass

    @transform()
    @set_flag.command()
    async def mention_prefix(self, interaction: Interaction, value: bool) -> None:
        pass

    @transform()
    @set_flag.command()
    async def color(self, interaction: Interaction, value: int) -> None:
        pass

    @transform("global")
    @app_commands.choices(
        type=[
            app_commands.Choice(name=activity_type.name, value=activity_type.name)
            for activity_type in discord.ActivityType
        ]
    )
    @set_flag.command()
    async def activity(
        self,
        interaction: Interaction,
        application_id: Optional[int],
        name: Optional[str],
        url: Optional[str],
        type: app_commands.Choice[str],
        state: Optional[str],
        details: Optional[str],
        platform: Optional[str],
    ) -> None:
        activity = discord.Activity(
            application_id=application_id,
            name=name,
            url=url,
            type=discord.ActivityType[type.value],
            state=state,
            details=details,
            platform=platform,
        )
        status = self.bot.status
        await self.bot.change_presence(status=status, activity=activity)
        self.bot.activity = activity

    @transform("global")
    @app_commands.choices(
        value=[
            app_commands.Choice(name=status.name, value=status.value)
            for status in discord.Status
        ]
    )
    @set_flag.command()
    async def status(self, interaction: Interaction, value: app_commands.Choice[str]):
        status = discord.Status[value.value]
        acitivity = self.bot.activity
        await self.bot.change_presence(status=status, activity=acitivity)  # type: ignore
        self.bot.status = status
