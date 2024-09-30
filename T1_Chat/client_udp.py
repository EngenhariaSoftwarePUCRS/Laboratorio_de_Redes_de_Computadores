from socket import *

from config import server_udp


clientSocket = socket(AF_INET, SOCK_DGRAM)


def main():
    while True:
        message = input('Input anycase sentence: ')

        clientSocket.sendto(message.encode(), server_udp)
        
        response, _ = clientSocket.recvfrom(2048)
        response = response.decode()

        print(response)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Client stopped')
    finally:
        clientSocket.close()
        exit(0)
