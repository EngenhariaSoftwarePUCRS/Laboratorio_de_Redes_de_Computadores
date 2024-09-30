from typing import Tuple


server_name = '127.0.0.1'
server_port_udp = 12000
server_udp = (server_name, server_port_udp)

ACK = 'ACK'
ACK_EMPTY = 'ACK (empty message)'
ACK_FILE = 'ACK (file sent)'
ACK_MSG = 'ACK (message sent)'
ACK_REG = 'ACK (client registered)'
ACK_UNREG = 'ACK (client unregistered)'
NACK = 'NACK'
NACK_INVALID = 'NACK (invalid message)'
NACK_NOT_FOUND = 'NACK (client not found)'

PREFIX_REG = '/REG'
PREFIX_MSG = '/MSG'
PREFIX_FILE = '/FILE'
PREFIX_QUIT = '/QUIT'
        
MESSAGE_MAX_SIZE_UDP = 1024

Address = Tuple[str, int]
