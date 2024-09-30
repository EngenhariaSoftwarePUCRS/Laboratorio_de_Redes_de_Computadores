import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from typing import Tuple

from clients import clients
from config import (
    ACK_EMPTY, ACK_FILE, ACK_MSG, ACK_REFRESH, ACK_REG, ACK_UNREG,
    NACK_INVALID,
    MAX_SERVER_CONNECTIONS, MESSAGE_MAX_SIZE_TCP,
    PREFIX_FILE, PREFIX_MSG, PREFIX_QUIT, PREFIX_REFRESH, PREFIX_REG, PREFIX_WHOAMI,
    Address, server_tcp,
)


server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_tcp)
# Allows the server to reuse the address and port, useful for developing, since the server can be restarted without waiting for the OS to release the port
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.listen(MAX_SERVER_CONNECTIONS)

sockets_list = [server_socket]
client_sockets: dict[socket, Address] = {}


def main():
    print(f'The server is ready to receive at {server_tcp}')

    read_sockets: list[socket]
    exception_sockets: list[socket]
    while True:
        # Waits for any of the sockets to be ready for reading
        readable_sockets, writeable_sockets, error_sockets = sockets_list, [], sockets_list
        read_sockets, _, exception_sockets = select.select(readable_sockets, writeable_sockets, error_sockets)

        for read_socket in read_sockets:
            if read_socket == server_socket:
                connection_socket, client = server_socket.accept()
                sockets_list.append(connection_socket)
                client_sockets[connection_socket] = client
            else:
                message, success = receive_message(read_socket)
                if not success:
                    sockets_list.remove(read_socket)
                    del client_sockets[read_socket]
                else:
                    client_address = client_sockets[read_socket]
                    handle_message(message, client_socket=read_socket, client_address=client_address)
        
        # Handle socket exceptions (e.g., closed clients)
        for exception_socket in exception_sockets:
            sockets_list.remove(exception_socket)
            exception_socket.close()
            del clients[exception_socket]


def receive_message(client: socket) -> Tuple[str, bool]:
    try:
        message = client.recv(MESSAGE_MAX_SIZE_TCP)
        message = message.decode()
        print(f'Received message: {message} from {client}')
        return message, True
    except Exception as e:
        print(f'An error occurred: {e}')
        return '', False
    

def handle_message(message: str, client_socket: socket, client_address: Address):
    if len(message) == 0:
        client_socket.send(ACK_EMPTY.encode())
        return

    if not message.startswith('/'):
        client_socket.send(NACK_INVALID.encode())
        return

    # Workaround to always split the message in two parts
    if ' ' not in message:
        message += ' '
    prefix, message = message.split(' ', 1)

    if prefix == PREFIX_REFRESH:
        client_socket.send(ACK_REFRESH.encode())
        return

    # If message starts with '/REG' add the client to the list of clients
    if prefix == PREFIX_REG:
        client_socket.send(ACK_REG.encode())
        register(nickname=message.strip(), address=client_address)
    
    # If message starts with '/WHOAMI' return the client's nickname, host and port
    elif prefix == PREFIX_WHOAMI:
        for client in clients:
            _nickname, address = client
            if address == client_address:
                client_socket.send(str(client).encode())
    
    # If message starts with '/MSG' send a message to all clients
    elif prefix == PREFIX_MSG:
        client_socket.send(ACK_MSG.encode())
        send_message(message, sender=client_address)

    # If message starts with '/FILE' send a file to all clients
    elif prefix == PREFIX_FILE:
        client_socket.send(ACK_FILE.encode())
        filename = receive_file(client_socket, sender=client_address)
        nickname = ""
        if message.startswith('@'):
            nickname = message.split(' ')[0]
        send_file(filename, sender=client_address, target=nickname)

    # If message starts with '/QUIT' remove the client from the list of clients
    elif prefix == PREFIX_QUIT:
        client_socket.send(ACK_UNREG.encode())
        unregister(address=client_address)

    else:
        print('Invalid message')
        client_socket.send(NACK_INVALID.encode())


def register(nickname: str, address: Address):
    print(f'{nickname} connected')
    clients.append((nickname, address))


def unregister(address: Address):
    # Remove the client from the list of clients
    for (nickname, address_db) in clients:
        if address_db == address:
            print(f'{nickname} disconnected')
            clients.remove((nickname, address))
            break


def send_message(message: str, sender: Address):
    if message.startswith('@'):
        nickname, message = message.split(' ', 1)
        print(f'Sending private message to {nickname}')
        for (nick, client_address) in clients:
            if f"@{nick}" == nickname:
                for client_socket, address in client_sockets.items():
                    if address == client_address:
                        client_socket.send(message.encode())
                break
    else:
        for client_socket, client_address in client_sockets.items():
            if client_address != sender:
                print(f'Sending message to {client_address}')
                client_socket.send(message.encode())


def receive_file(client: socket, sender: Address) -> str:
    try:
        filename = client.recv(MESSAGE_MAX_SIZE_TCP).decode()
        filename = f"{filename}.temp"
        print(f'Received file: {filename} from {sender}')
        with open(filename, 'wb') as file:
            while (data := client.recv(MESSAGE_MAX_SIZE_TCP)) != b'EOF':
                file.write(data)
        print(f'File {filename} saved')
        return filename

    except Exception as e:
        print(f'An error occurred while reading the file: {e}')


def send_file(filename: str, sender: Address, target: str = ''):
    # Future bug: if the file name starts with '@', it will be treated as a nickname
    if target:
        print(f'Sending file privately to {target}')
        for (nickname, client_address) in clients:
            if f"@{nickname}" == target:
                with open(filename, 'rb') as file:
                    for client_socket, address in client_sockets.items():
                        if address == client_address:
                            client_socket.send(filename.encode())
                            while (file_data := file.read(MESSAGE_MAX_SIZE_TCP)):
                                client_socket.send(file_data)
                            client_socket.send(b'EOF')
                            break
                break
    else:
        for client_socket, client_address in client_sockets.items():
            if client_address != sender:
                with open(filename, 'rb') as file:
                    client_socket.send(filename.encode())
                    while (file_data := file.read(MESSAGE_MAX_SIZE_TCP)):
                        client_socket.send(file_data)
                    client_socket.send(b'EOF')


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
