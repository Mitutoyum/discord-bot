from discord import Intents
from pathlib import Path

intents = Intents.all()
resources = Path(__file__).parents[1] / 'resources'
cogs_dir = Path(__file__).parents[1] / 'cogs'
config_path = resources / 'config.json'
database_path = resources / 'database.db'

def init() -> None:
    if not config_path.is_file():
        config_path.write_text('{}')