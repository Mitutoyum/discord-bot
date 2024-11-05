import typer
import discord

from core.bot import Bot
from core.tree import Tree
from dotenv import load_dotenv
from core import utils, config, database

import logging
import asyncio
from os import getenv
from typing import Annotated

handler = logging.FileHandler('discord.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', '{'))

discord.utils.setup_logging()
logging.root.addHandler(handler)


logger = logging.getLogger(__name__)
app = typer.Typer(no_args_is_help=True, add_completion=False)

@app.command()
def setup():
    if not config.config_path.is_file():
        config.config_path.write_text('{}')
        logger.info('Initialized config')
    if not config.database_path.is_file():
        database.init()

    suffix = '\n>'
    prefix = typer.prompt(
        text = '\nWhat prefix do you want to use?',
        type = str,
        prompt_suffix = suffix
    )
    bot_token = typer.prompt(
        text = '\nEnter the token of your bot application (input will be hidden)',
        type = str,
        hide_input = True,
        prompt_suffix = suffix
    )
    config.set_flag('global.prefix', prefix)

    with open('.env', 'w', encoding='utf-8') as file:
        file.write(f'BOT_TOKEN={bot_token}')

    typer.secho('Setup completed, you can now run the bot', fg=typer.colors.GREEN)

@app.command()
def run():
    bot = Bot(
        command_prefix=utils.get_prefix,
        intents=config.intents,
        tree_cls=Tree,
        help_command=None,
        activity=config.activity,
        status=config.status
    )

    logger.info('Starting bot.')

    load_dotenv()
    bot.run(getenv('BOT_TOKEN'), log_handler=None)
    asyncio.run(database.close_all())



@app.command()
def set_token(token: Annotated[str, typer.Argument()]):
    with open('.env', 'w', encoding='utf-8') as file:
        file.write(f'BOT_TOKEN={token}')
    typer.secho('Token has been changed', fg=typer.colors.GREEN)

        

if __name__ == '__main__':
    app()