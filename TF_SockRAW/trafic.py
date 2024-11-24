import socket
import struct
import datetime

def parse_packet(packet):
    """Analisa pacotes DNS e HTTP para capturar informações de navegação."""
    ethernet_header = packet[:14]
    ip_header = packet[14:34]
    protocol = ip_header[9]

    if protocol == 6:  # TCP (HTTP)
        tcp_header = packet[34:54]
        src_ip = socket.inet_ntoa(ip_header[12:16])
        dest_ip = socket.inet_ntoa(ip_header[16:20])

        # Verifica se é uma requisição HTTP
        if b"GET" in packet or b"POST" in packet:
            data = packet[54:].decode(errors="ignore")
            url_start = data.find("Host: ") + len("Host: ")
            url_end = data.find("\r\n", url_start)
            host = data[url_start:url_end]
            return src_ip, host, "http"

    elif protocol == 17:  # UDP (DNS)
        dns_data = packet[42:]
        query = dns_data[12:].split(b"\x00")[0]
        domain = query.decode(errors="ignore")
        src_ip = socket.inet_ntoa(ip_header[12:16])
        return src_ip, domain, "dns"

    return None

def start_sniffer():
    """Inicia o sniffer e salva o histórico de navegação."""
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003)) as sock:
        while True:
            packet, _ = sock.recvfrom(65565)
            parsed = parse_packet(packet)
            if parsed:
                src_ip, data, protocol = parsed
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp} - {src_ip} - {protocol} - {data}")

# Teste
if __name__ == "__main__":
    start_sniffer()
