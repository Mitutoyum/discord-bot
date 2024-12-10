import aiohttp
import discord

from datetime import datetime

from core.bot import Bot
from core.utils.cog import Cog
from core.utils.message import Messenger
from core.utils.embeds import BaseEmbed
from discord import Interaction, app_commands


class Roblox(Cog, description='Roblox utilities'):


    @app_commands.command()
    async def userinfo(self, interaction: Interaction, user: str) -> None:
        embed = BaseEmbed(interaction.user, interaction.guild_id)
        embed.title = f'Showing userinfo: `{user}`'

        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            if not user.isdigit():
                payload = {
                    "usernames": [
                        user
                    ],
                    'excludeBannedUsers': False
                }
                async with session.post('https://users.roblox.com/v1/usernames/users', json=payload) as response:
                    user = (await response.json())['data'][0]['id']

            async with session.get(f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user}&size=720x720&format=Png&isCircular=false') as response:
                response = await response.json()
                embed.set_thumbnail(url=response['data'][0]['imageUrl'])

            async with session.get(f'https://users.roblox.com/v1/users/{user}') as response:
                response = await response.json()
                embed.description = f'```{response['description'] or 'No description'}```'

                embed.add_field(name='> Username', value=f'`{response['name']}`')
                embed.add_field(name='> UserId', value=f'`{response['id']}`')
                embed.add_field(name='> Display Name', value=f'`{response['displayName']}`')

                embed.add_field(name='> Join Date', value=discord.utils.format_dt(datetime.fromisoformat(response['created'])))
                embed.add_field(name='> Banned', value=response['isBanned'])
                embed.add_field(name='> Verified Badge', value=response['hasVerifiedBadge'])

        await Messenger(interaction, use_embed_check=False).followup_send(embed=embed)

