from typing import Literal

from config import PREFIX_FILE, PREFIX_MSG, PREFIX_QUIT, PREFIX_REFRESH, PREFIX_REG


color_mapper = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'concealed': '\033[8m'
}


def print_reg(*args, **kwargs):
    print_('blue', *args, **kwargs)


def print_msg(*args, **kwargs):
    print_('green', *args, **kwargs)


def print_file(*args, **kwargs):
    print_('yellow', *args, **kwargs)


def print_quit(*args, **kwargs):
    print_('red', *args, **kwargs)


def print_(color: Literal['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset', 'bold', 'underline', 'blink', 'reverse', 'concealed'], *args, **kwargs):
    print(color_mapper[color], end='')
    print(*args, **kwargs)
    print(color_mapper['reset'], end='')


def get_print(message: str) -> callable:
    if message.startswith(PREFIX_REG):
        return print_reg
    if message.startswith(PREFIX_MSG):
        return print_msg
    if message.startswith(PREFIX_FILE):
        return print_file
    if message.startswith(PREFIX_QUIT):
        return print_quit
    return print

    
def print_options():
    print("Options:")
    print_reg(f"{PREFIX_REG} <nickname>: Register with the server")
    print_msg(f"{PREFIX_MSG} <message>: Send a message to all clients")
    print_msg(f"{PREFIX_MSG} @<nickname> <message>: Send a private message to a client")
    print_("white", f"{PREFIX_REFRESH}: Refresh to check for new messages")
    print_file(f"{PREFIX_FILE} <file>: Send a file to all clients")
    print_file(f"{PREFIX_FILE} @<nickname> <file>: Send a file to a client")
    print_quit(f"{PREFIX_QUIT}: Disconnect from the server")
    print()
