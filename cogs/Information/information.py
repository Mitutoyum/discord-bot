from .. import Cog
from typing import Optional

from discord import app_commands, Interaction
from discord.ext import commands

from core.utils import config_manager, helpers, embeds, views
from core.utils.message import Messenger

from inspect import _empty as empty

class Information(Cog):

    @app_commands.command(description='Shows help')
    async def help(self, interaction: Interaction, command: Optional[str] = None):
        embed = embeds.BaseEmbed(interaction.user)
        message_utils = Messenger(interaction, use_embed_check=False)
        prefix = config_manager.get_flag(f'servers.{interaction.guild_id}.prefix', None)

        if not command:
            embed.title = 'Help Center'
            embed.description = f'```Select a category to begin```\nServer\'s prefix: `{prefix}`'
            embed.add_field(
                name='> About the bot',
                value=f'- {self.bot.user.name} is a open source multi-functional bot, see more at [github](https://github.com/)'
            )
            view = views.BaseView(interaction.user)
            view.add_item(views.HelpCategorySelect(self.bot))
            await message_utils.reply(embed=embed, view=view)

        else:
            command = self.bot.get_command(command) or self.bot.tree.get_command(command)
            embed.title = f'Showing command: `{command.qualified_name}`'
            embed.description = f'```{command.description}```'
            types = []
            flags = await self.bot.tree.get_mention(command) or f'{prefix}{command.qualified_name} ' + ' '.join([
                f'<{name}>'
                if properties['default'] is empty else
                f'[{name}]'
                for name, properties in helpers.get_params(command.callback).items()
            ])

            if isinstance(command, commands.Group):
                types.append('`Group`')
            elif isinstance(command, commands.HybridGroup):
                types.append('`Hybrid Group`')
            elif isinstance(command, app_commands.Group):
                types.append('`Application Group`')
            elif command in self.bot.commands:
                types.append('`Prefix command`')
            elif command.qualified_name in self.bot.tree._global_commands:
                types.append('`Application command`')

            embed.add_field(name='> Category', value=f'`{getattr(command, 'cog_name', None) or (await self.bot.tree.get_cog(command.name)).qualified_name}`')
            embed.add_field(name='> Type', value=' '.join(types))
            embed.add_field(name='> Usage', value=flags)
            await message_utils.reply(embed=embed)

    
    @app_commands.command(description='Show the bot\'s latency')
    async def ping(self, interaction: Interaction):
        await Messenger(interaction).reply(f'Bot\'s latency: {round(self.bot.latency * 1000)}ms')