#!/usr/bin/python3
import socket
import struct
import time
import sys
from ipaddress import IPv4Network
import threading

# Estrutura do cabeçalho IP
class IP:
    def __init__(self, source, destination):
        self.version = 4
        self.ihl = 5
        self.tos = 0
        self.tot_len = 20 + 8
        self.id = 54321
        self.frag_off = 0
        self.ttl = 255
        self.protocol = socket.IPPROTO_ICMP
        self.check = 0
        self.saddr = socket.inet_aton(source)
        self.daddr = socket.inet_aton(destination)

# Estrutura do pacote ICMP
class ICMP:
    def __init__(self):
        self.type = 8
        self.code = 0
        self.checksum = 0
        self.id = 12345
        self.sequence = 1

def calculate_checksum(data):
    s = 0
    n = len(data)
    for i in range(0, n, 2):
        if i + 1 < n:
            a = data[i]
            b = data[i + 1]
            s = s + (a + (b << 8))
        elif i < n:
            s = s + data[i]
    s = s + (s >> 16)
    s = ~s & 0xffff
    return s

class NetworkScanner:
    def __init__(self, network, timeout):
        self.network = network
        self.timeout = timeout
        self.active_hosts = []
        self.lock = threading.Lock()

    def create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            return s
        except socket.error as e:
            print(f"Socket creation error: {e}")
            sys.exit()

    def create_packet(self, dst_ip):
        # Criar cabeçalho IP
        ip = IP(socket.gethostbyname(socket.gethostname()), dst_ip)
        
        # Criar pacote ICMP
        icmp = ICMP()
        
        # Montar pacote
        packet = struct.pack("!BBHHHBBH4s4s", 
            (ip.version << 4) + ip.ihl, ip.tos, ip.tot_len,
            ip.id, ip.frag_off, ip.ttl, ip.protocol, ip.check,
            ip.saddr, ip.daddr)
        
        icmp_packet = struct.pack("!BBHHH", 
            icmp.type, icmp.code, icmp.checksum,
            icmp.id, icmp.sequence)
        
        # Calcular checksum
        icmp_checksum = calculate_checksum(icmp_packet)
        
        # Remontar pacote ICMP com checksum
        icmp_packet = struct.pack("!BBHHH",
            icmp.type, icmp.code, icmp_checksum,
            icmp.id, icmp.sequence)
        
        return packet + icmp_packet

    def scan_host(self, ip):
        sock = self.create_socket()
        packet = self.create_packet(ip)
        
        start_time = time.time()
        sock.sendto(packet, (ip, 0))
        
        try:
            sock.settimeout(self.timeout / 1000)  # Converter para segundos
            data, addr = sock.recvfrom(1024)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Converter para ms
            
            with self.lock:
                self.active_hosts.append((ip, response_time))
        
        except socket.timeout:
            pass
        finally:
            sock.close()

    def scan(self):
        threads = []
        start_time = time.time()
        
        # Criar threads para cada host
        for ip in IPv4Network(self.network):
            if ip == IPv4Network(self.network).network_address or \
               ip == IPv4Network(self.network).broadcast_address:
                continue
                
            t = threading.Thread(target=self.scan_host, args=(str(ip),))
            threads.append(t)
            t.start()
        
        # Aguardar todas as threads terminarem
        for t in threads:
            t.join()
            
        end_time = time.time()
        
        # Ordenar resultados por IP
        self.active_hosts.sort(key=lambda x: socket.inet_aton(x[0]))
        
        # Imprimir resultados
        print("\nResultados da varredura:")
        print(f"Rede escaneada: {self.network}")
        print(f"Tempo total: {(end_time - start_time):.2f} segundos")
        print(f"Hosts ativos: {len(self.active_hosts)}")
        print(f"Total de hosts na rede: {IPv4Network(self.network).num_addresses - 2}")
        print("\nHosts ativos encontrados:")
        for ip, response_time in self.active_hosts:
            print(f"{ip}: {response_time:.2f}ms")

def main():
    if len(sys.argv) != 3:
        print("Uso: ./scanner.py <rede/mascara> <timeout_ms>")
        print("Exemplo: ./scanner.py 192.168.1.0/24 1000")
        sys.exit(1)

    network = sys.argv[1]
    timeout = int(sys.argv[2])

    scanner = NetworkScanner(network, timeout)
    scanner.scan()

if __name__ == "__main__":
    main()