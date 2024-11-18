import socket
import sys

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()


if __name__ == '__main__':
    # Based on https://www.binarytides.com/raw-socket-programming-in-python-linux/
    main()
