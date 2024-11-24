#!/usr/bin/python3
import socket
import struct
import time
from datetime import datetime
import sys

class PacketSniffer:
    def __init__(self, interface):
        self.interface = interface
        self.history = []
        self.dns_cache = {}

    def create_socket(self):
        try:
            # Criar socket raw
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
            sock.bind((self.interface, 0))
            return sock
        except socket.error as e:
            print(f"Erro ao criar socket: {e}")
            sys.exit(1)

    def parse_ethernet_header(self, packet):
        eth_length = 14
        eth_header = packet[:eth_length]
        eth = struct.unpack('!6s6sH', eth_header)
        return socket.ntohs(eth[2]), packet[eth_length:]

    def parse_ip_header(self, packet):
        ip_header = packet[:20]
        iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
        
        version_ihl = iph[0]
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])
        
        return protocol, s_addr, d_addr, packet[iph_length:]

    def parse_tcp_header(self, packet):
        tcp_header = packet[:20]
        tcph = struct.unpack('!HHLLBBHHH', tcp_header)
        
        source_port = tcph[0]
        dest_port = tcph[1]
        sequence = tcph[2]
        acknowledgement = tcph[3]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4
        
        return source_port, dest_port, packet[tcph_length*4:]

    def parse_udp_header(self, packet):
        udph_length = 8
        udp_header = packet[:udph_length]
        udph = struct.unpack('!HHHH', udp_header)
        
        source_port = udph[0]
        dest_port = udph[1]
        
        return source_port, dest_port, packet[udph_length:]

    def parse_dns_packet(self, data):
        try:
            # Parsing simplificado do cabeçalho DNS
            dns_header = struct.unpack('!HHHHHH', data[:12])
            qcount = dns_header[2]
            
            # Pular cabeçalho
            offset = 12
            
            # Processar queries
            for _ in range(qcount):
                qname = []
                while True:
                    length = data[offset]
                    offset += 1
                    if length == 0:
                        break
                    qname.append(data[offset:offset+length].decode())
                    offset += length
                
                domain = '.'.join(qname)
                return domain
                
        except Exception:
            return None

    def parse_http_request(self, data):
        try:
            # Decodificar dados HTTP
            http_data = data.decode('utf-8')
            
            # Procurar por requisições GET ou POST
            lines = http_data.split('\n')
            for line in lines:
                if line.startswith('GET') or line.startswith('POST'):
                    # Extrair URL
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]
            return None
        except:
            return None

    def save_history(self):
        with open('historico.html', 'w') as f:
            f.write('''<html>
<header>
<title>Historico de Navegacao</title>
</header>
<body>
<ul>
''')
            
            for entry in self.history:
                f.write(f'<li>{entry}</li>\n')
            
            f.write('''</ul>
</body>
</html>''')

    def start_sniffing(self):
        sock = self.create_socket()
        
        try:
            while True:
                packet = sock.recvfrom(65535)[0]
                
                # Parse Ethernet
                eth_protocol, data = self.parse_ethernet_header(packet)
                
                # Se não for IP, continuar
                if eth_protocol != 0x0800:
                    continue
                
                # Parse IP
                protocol, src_ip, dst_ip, data = self.parse_ip_header(data)
                
                # Processar DNS (UDP porta 53)
                if protocol == 17:  # UDP
                    src_port, dst_port, data = self.parse_udp_header(data)
                    if dst_port == 53:  # DNS
                        domain = self.parse_dns_packet(data)
                        if domain:
                            self.dns_cache[dst_ip] = domain
                
                # Processar HTTP (TCP porta 80)
                elif protocol == 6:  # TCP
                    src_port, dst_port, data = self.parse_tcp_header(data)
                    if dst_port == 80:  # HTTP
                        url = self.parse_http_request(data)
                        if url:
                            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
                            hostname = self.dns_cache.get(dst_ip, dst_ip)
                            entry = f'{timestamp} - {src_ip} - <a href="http://{hostname}{url}">http://{hostname}{url}</a>'
                            self.history.append(entry)
                            self.save_history()
                
        except KeyboardInterrupt:
            print("\nCaptura finalizada")
            sock.close()

def main():
    if len(sys.argv) != 2:
        print("Uso: ./sniffer.py <interface>")
        print("Exemplo: ./sniffer.py eth0")
        sys.exit(1)

    sniffer = PacketSniffer(sys.argv[1])
    sniffer.start_sniffing()

if __name__ == "__main__":
    main()