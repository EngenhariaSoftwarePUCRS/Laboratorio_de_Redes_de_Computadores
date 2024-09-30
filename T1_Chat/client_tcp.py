from socket import socket, AF_INET, SOCK_STREAM

from config import ACK_UNREG, MESSAGE_MAX_SIZE_TCP, PREFIX_FILE, PREFIX_QUIT, server_tcp
from print import get_print, print_, print_file, print_options, print_quit


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

            if message == PREFIX_QUIT:
                send_message(message)
                response = client_socket.recv(MESSAGE_MAX_SIZE_TCP).decode()
                if response == ACK_UNREG:
                    print_quit("Disconnected from the server.")
                    break
            else:
                send_message(message)

            # Receive and print the server's response
            response = client_socket.recv(MESSAGE_MAX_SIZE_TCP)
            response = response.decode()
            print_server = get_print(response)
            print_server(response)

    except Exception as e:
        print_("red", f"An error occurred: {e}")

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
            print_file(f"Sending file {filename}")
            # Send the file name
            client_socket.send(first_line.encode())
            # Send the file content
            while file_data := file.read(MESSAGE_MAX_SIZE_TCP):
                client_socket.send(file_data)
            # Send EOF to indicate the end of the file
            client_socket.send(b'EOF')
            print_file(f"File {filename} sent.")

    except FileNotFoundError as e:
        print_file(f"File not found: {e}")


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
