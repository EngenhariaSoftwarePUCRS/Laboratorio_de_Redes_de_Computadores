from typing import Literal


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

def print_error(*args, **kwargs):
    print_(color='red', *args, **kwargs)

def print_(color: Literal['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset', 'bold', 'underline', 'blink', 'reverse', 'concealed'], *args, **kwargs):
    print(color_mapper[color], end='')
    print(*args, **kwargs)
    print(color_mapper['reset'], end='')
