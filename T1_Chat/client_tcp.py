from socket import socket, AF_INET, SOCK_STREAM

from menu import print_options
from config import ACK_UNREG, MESSAGE_MAX_SIZE_TCP, PREFIX_FILE, server_tcp


client_socket = socket(AF_INET, SOCK_STREAM)


def main():
    try:
        client_socket.connect(server_tcp)
        print(f"Connected to server at {server_tcp}")

        while True:
            print_options()

            message = ""
            while message.strip() == "":
                message = input().lstrip()

            if message == '/QUIT':
                send_message(message)
                response = client_socket.recv(MESSAGE_MAX_SIZE_TCP).decode()
                if response == ACK_UNREG:
                    print("Disconnected from the server.")
                    break
            else:
                send_message(message)

            # Receive and print the server's response
            response = client_socket.recv(MESSAGE_MAX_SIZE_TCP)
            print(f"Server response: {response.decode()}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client_socket.close()
        print("Connection closed.")


def send_message(message: str):
    if message.startswith(PREFIX_FILE):
        send_file(message)
    else:
        client_socket.send(message.encode())


def send_file(message: str):
    _prefix, to = message.split(' ', 1)

    if to.startswith('@'):
        to = to.split(' ')[0]
        first_line = f'{PREFIX_FILE} {to}'
    else:
        first_line = PREFIX_FILE
    
    filename = message.removeprefix(first_line).strip()

    try:
        with open(filename, 'rb') as file:
            print(f"Sending file {filename}")
            # Send the file name
            client_socket.send(first_line.encode())
            # Send the file content
            while file_data := file.read(MESSAGE_MAX_SIZE_TCP):
                client_socket.send(file_data)
            # Send EOF to indicate the end of the file
            client_socket.send(b'EOF')
            print(f"File {filename} sent.")

    except FileNotFoundError as e:
        print(f"File not found: {e}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Client stopped')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        client_socket.close()
        print('Connection closed.')
