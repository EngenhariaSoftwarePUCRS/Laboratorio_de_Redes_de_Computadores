from socket import socket, AF_INET, SOCK_DGRAM

from clients import clients
from config import (
    ACK_EMPTY, ACK_MSG, ACK_REG, ACK_UNREG,
    MESSAGE_MAX_SIZE_UDP,
    NACK_INVALID,
    PREFIX_FILE, PREFIX_MSG, PREFIX_QUIT, PREFIX_REG,
    server_udp,
)


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(server_udp)


def main():
    print(f'The server is ready to receive at {server_udp}')

    while True:
        message, client = server_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        message = message.decode()
        print(f'Received message: {message} from {client}')

        if len(message) == 0:
            server_socket.sendto(ACK_EMPTY.encode(), client)
            continue

        if not message.startswith('/'):
            server_socket.sendto(NACK_INVALID.encode(), client)
            continue

        # Workaround to always split the message in two parts
        if ' ' not in message:
            message += ' '
        prefix, message = message.split(' ', 1)

        # If message starts with '/REG' add the client to the list of clients
        if prefix == PREFIX_REG:
            nickname = message
            print(f'{nickname} connected')
            clients.append((nickname, client))
            server_socket.sendto(ACK_REG.encode(), client)
        
        # If message starts with '/MSG' send a message to all clients
        elif prefix == PREFIX_MSG:
            if message.startswith('@'):
                nickname, message = message.split(' ', 1)
                print(f'Sending message to {nickname}')
                for (nick, address) in clients:
                    if f"@{nick}" == nickname:
                        server_socket.sendto(message.encode(), address)
                        break
                server_socket.sendto(ACK_MSG.encode(), client)
            else:
                for client in clients:
                    print(f'Sending message to {client}')
                    _nickname, address = client
                    server_socket.sendto(message.encode(), address)
            continue

        # If message starts with '/FILE' send a file to all clients
        elif prefix == PREFIX_FILE:
            # Future bug: if the file name starts with '@', it will be treated as a nickname
            if message.startswith('@'):
                nickname = message.split(' ')[0]
                print(f'Sending file to {nickname}')
                for (nick, address) in clients:
                    if f"@{nick}" == nickname:
                        file = message.removeprefix(f'{nickname} ')
                        server_socket.sendto(file.encode(), address)
                        break
                server_socket.sendto(ACK_MSG.encode(), client)
            else:
                for client in clients:
                    print(f'Sending file to {client}')
                    _nickname, address = client
                    file = message
                    server_socket.sendto(message.encode(), address)

        # If message starts with '/QUIT' remove the client from the list of clients
        elif prefix == PREFIX_QUIT:
            # Remove the client from the list of clients
            for (nickname, address) in clients:
                if address == client:
                    print(f'{nickname} disconnected')
                    clients.remove((nickname, address))
                    break
            server_socket.sendto(ACK_UNREG.encode(), client)

        else:
            print('Invalid message')
            server_socket.sendto(NACK_INVALID.encode(), client)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Server stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        server_socket.close()
        exit(0)
