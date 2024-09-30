from socket import socket, AF_INET, SOCK_DGRAM

from clients import clients
from config import server_udp


server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(server_udp)


def main():
    print(f'The server is ready to receive at {server_udp}')

    while True:
        message, client = server_socket.recvfrom(2048)
        message = message.decode()
        print(f'Received message: {message} from {client}')

        prefix, message = message.split(' ', 1)

        # If message starts with add the client to the list of clients
        if prefix == '/REG':
            nickname = message
            print(f'{nickname} connected')
            clients.append((nickname, client))
            server_socket.sendto('ACK (client registered)'.encode(), client)
        
        # If message starts with send a message to all clients
        elif prefix == '/MSG':
            for client in clients:
                print(f'Sending message to {client}')
                _nickname, address = client
                server_socket.sendto(message.encode(), address)
            continue

        else:
            print('Invalid message')
            server_socket.sendto('-NACK'.encode(), client)


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
