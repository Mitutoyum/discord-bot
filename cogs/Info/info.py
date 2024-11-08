from .. import Cog
from typing import Optional

from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.ext.commands import Context

from core import config
from core.utils import helpers, embeds, views
from core.utils.helpers import MessageUtils

from inspect import _empty as empty

class Info(Cog):

    @app_commands.command(description='Shows help')
    async def help(self, inter: Interaction, command: Optional[str] = None):
        embed = embeds.BaseEmbed(inter.user)
        message_utils = MessageUtils(inter, use_embed_check=False)
        prefix = config.get_flag(f'servers.{inter.guild_id}.prefix', None)

        if not command:
            embed.title = 'Help Center'
            embed.description = f'```Select a category to begin```\nServer\'s prefix: `{prefix}`'
            embed.add_field(
                name='> About the bot',
                value=f'- {self.bot.user.name} is a open source multi-functional bot, see more at [github](https://github.com/)'
            )
            view = views.BaseView(inter.user)
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
                for name, properties in helpers.get_flags(command.callback).items()
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


    @help.autocomplete('command')
    async def help_autocompletion(self, inter: Interaction, current: str):
        cmds = []
        for cmd in self.bot.walk_commands():
            cmds.append(app_commands.Choice(name=cmd.qualified_name, value=cmd.qualified_name))
        
        for cmd in self.bot.tree.walk_commands():
            cmds.append(app_commands.Choice(name=cmd.qualified_name, value=cmd.qualified_name))
        
        return cmds
    
    @app_commands.command(description='Show the bot\'s latency')
    async def ping(self, interaction: Interaction):
        await MessageUtils(interaction).reply(content=f'```Bot\'s latency: {round(self.bot.latency * 1000)}ms```')