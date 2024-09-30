from sys import argv
from socket import socket, AF_INET, SOCK_DGRAM

from config import ACK_UNREG, MESSAGE_MAX_SIZE_UDP, PREFIX_FILE, Address, server_udp


client_socket = socket(AF_INET, SOCK_DGRAM)


def main(address: Address):
    client_socket.bind(address)
    while True:
        message = input('Input anycase sentence (or enter to update): ')

        send_message(message)
        
        response, _ = client_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        response = response.decode()

        print(response)

        if response == ACK_UNREG:
            break


def send_message(message: str):
    if not message.startswith(PREFIX_FILE):
        client_socket.sendto(message.encode(), server_udp)
    else:
        _prefix, to = message.split(' ', 1)
        if to.startswith('@'):
            to = to.split(' ')[0]
            first_line = f'{PREFIX_FILE} {to}'
        else:
            first_line = PREFIX_FILE
        filename = message.removeprefix(first_line).strip()
        file = open(filename, 'rb')
        message = f"{first_line} {file.read()}"
        client_socket.sendto(message.encode(), server_udp)


if __name__ == '__main__':
    try:
        try:
            port = int(argv[1])
        except IndexError:
            print('Port number not provided')
        except ValueError:
            print('Invalid port number')
        else:
            main(port)
    except KeyboardInterrupt:
        print('Client stopped')
    except FileNotFoundError as e:
        print(f'File not found: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        client_socket.close()
