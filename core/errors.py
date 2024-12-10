

class BotException(Exception):
    '''The Base exception type for all custom exceptions of this bot'''

class NotServerOwner(BotException):
    '''Exception raised when the message author is not the owner of the server.'''

class GuildOnly(BotException): # I prefer this name
    '''Replacement for commands.NoPrivateMessage'''