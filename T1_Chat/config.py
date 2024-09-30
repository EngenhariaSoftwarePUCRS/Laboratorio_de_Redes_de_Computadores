from typing import Tuple


server_name = '127.0.0.1'
server_port_udp = 12000
server_udp = (server_name, server_port_udp)
server_port_tcp = 13000
server_tcp = (server_name, server_port_tcp)

ACK = 'ACK'
ACK_EMPTY = 'ACK (empty message)'
ACK_FILE = 'ACK (file sent)'
ACK_MSG = 'ACK (message sent)'
ACK_REFRESH = 'ACK (refreshed)'
ACK_REG = 'ACK (client registered)'
ACK_UNREG = 'ACK (client unregistered)'
NACK = 'NACK'
NACK_INVALID = 'NACK (invalid message)'
NACK_NOT_FOUND = 'NACK (client not found)'

MAX_SERVER_CONNECTIONS = 5

MESSAGE_MAX_SIZE_TCP = 1024
MESSAGE_MAX_SIZE_UDP = 1024

PREFIX_FILE = '/FILE'
PREFIX_MSG = '/MSG'
PREFIX_QUIT = '/QUIT'
PREFIX_REFRESH = '/REFRESH'
PREFIX_REG = '/REG'

Address = Tuple[str, int]
