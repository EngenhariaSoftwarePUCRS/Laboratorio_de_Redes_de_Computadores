from sys import argv
from socket import socket, AF_INET, SOCK_DGRAM

from config import ACK_UNREG, MESSAGE_MAX_SIZE_UDP, PREFIX_FILE, server_udp


client_socket = socket(AF_INET, SOCK_DGRAM)


def main():
    while True:
        message = input('Input anycase sentence (or enter to update): ')

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
        
        response, _ = client_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        response = response.decode()

        print(response)

        if response == ACK_UNREG:
            break


if __name__ == '__main__':
    try:
        try:
            port = int(argv[1])
            client_socket.bind(('localhost', port))
        except IndexError:
            print('Port number not provided')
        except ValueError:
            print('Invalid port number')
        else:
            main()
    except KeyboardInterrupt:
        print('Client stopped')
    except FileNotFoundError as e:
        print(f'File not found: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        client_socket.close()
