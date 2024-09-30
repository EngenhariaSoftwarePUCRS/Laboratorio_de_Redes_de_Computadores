from sys import argv
from socket import socket, AF_INET, SOCK_DGRAM

from config import ACK_UNREG, MESSAGE_MAX_SIZE_UDP, PREFIX_FILE, PREFIX_QUIT, Address, server_udp
from print import get_print, print_file, print_options, print_quit


client_socket = socket(AF_INET, SOCK_DGRAM)


def main(address: Address | int):
    if isinstance(address, int):
        address = ('localhost', address)
    client_socket.bind(address)
    while True:
        print_options()

        message = ""
        while message.strip() == "":
            message = input().lstrip()

        if message == PREFIX_QUIT:
            send_message(message)
            response, _ = client_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
            if response.decode() == ACK_UNREG:
                print_quit("Disconnected from the server.")
                break
        else:
            send_message(message)
        
        response, _ = client_socket.recvfrom(MESSAGE_MAX_SIZE_UDP)
        response = response.decode()

        print_server = get_print(response)
        print_server(response)


def send_file_udp(client_socket, server_address, file_path):
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    client_socket.sendto(f"FILE: {filename}".encode(), server_address)
    client_socket.sendto(str(filesize).encode(), server_address)

    with open(file_path, "rb") as f:
        while(chunk := f.read(4096)):
            client_socket.sendto(chunk, server_address)
    
    print(f"Arquivo {filename} enviado com sucesso.")

def receive_file(client_socket):
    while True:
        data, server_address = client_socket.recvfrom(4096)

        if data.startswith(b"FILE:"):
            # Receive file name
            filename = data[5:].decode('utf-8')
            print(f"Receiving file: {filename}")

        filesize, _ = client_socket.recvfrom(4096)
        filesize = int(filesize.decode('utf-8'))
        print(f"Tamanho do arquivo: {filesize} bytes")

        with open(f"received_{filename}", "wb") as f:
            bytes_received = 0
            while bytes_received < filesize:
                file_data, _ = client_socket.recvfrom(4096)
                f.write(file_data)
                bytes_received += len(file_data)
        
        print(f"File {filename} successfully received!")

        with open(f"received_{filename}", "r") as f:
            content = f.read()
            print(content)

def send_message(message: str):
    if message.startswith(PREFIX_FILE):
        send_file(message)
    else:
        client_socket.sendto(message.encode(), server_udp)
    

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
            # Send file name
            client_socket.sendto(message.encode(), server_udp)
            # Send file content
            while file_data := file.read(MESSAGE_MAX_SIZE_UDP):
                client_socket.sendto(file_data, server_udp)
            # Send EOF to indicate the end of the file
            client_socket.sendto(b'EOF', server_udp)
            print_file(f"File {filename} sent")
    
    except FileNotFoundError as e:
        print(f'File not found: {e}')


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
