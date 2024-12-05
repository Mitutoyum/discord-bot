import getpass
from core.utils import config_manager
from core import database, config


def main():
    database.init()
    config.init()

    token = getpass.getpass('Enter your bot token: ')
    prefix = input('Choose a prefix for your bot: ')

    with open('.env', 'w', encoding='utf-8') as file:
        file.write(f'BOT_TOKEN={token}')
    
    config_manager.set_flag('global.prefix', prefix)

    print('Setup completed')


if __name__ == '__main__':
    main()