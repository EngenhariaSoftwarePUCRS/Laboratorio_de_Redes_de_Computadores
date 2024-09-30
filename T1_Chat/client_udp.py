from sys import argv
from socket import socket, AF_INET, SOCK_DGRAM

from config import server_udp


client_socket = socket(AF_INET, SOCK_DGRAM)


def main():
    while True:
        message = input('Input anycase sentence (or enter to update): ')

        client_socket.sendto(message.encode(), server_udp)
        
        response, _ = client_socket.recvfrom(2048)
        response = response.decode()

        print(response)


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
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        client_socket.close()
        exit(0)
