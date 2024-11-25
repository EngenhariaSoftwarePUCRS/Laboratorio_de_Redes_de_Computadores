import socket
import struct
import sys
import threading
import time
from ipaddress import IPv4Network


class IP:
    """IP Header Structure"""
    def __init__(self, source, destination):
        self.version = 4
        self.ihl = 5 # Internet Header Length
        self.tos = 0 # Type of Service
        self.tot_len = 20 + 8 # IP + ICMP (kernel should fill the correct total length)
        self.id = 54321 # Id of this packet
        self.frag_off = 0 # Fragmentation offset
        self.ttl = 255 # Time to live
        self.protocol = socket.IPPROTO_ICMP # Protocol
        self.check = 0 # Kernel will fill the correct checksum
        self.saddr = socket.inet_aton(source) # Spoof the source IP address if you want to
        self.daddr = socket.inet_aton(destination) # Destination IP


class ICMP:
    """ICMP Header Structure"""
    def __init__(self):
        self.type = 8 # ICMP type (8 = request, 0 = reply)
        self.code = 0
        self.checksum = 0 # Kernel will fill the correct checksum
        self.id = 12345
        self.sequence = 1


def calculate_checksum(data):
    """Calculate checksum for a given data"""
    checksum = 0

    data_length = len(data)
    for i in range(0, data_length, 2):
        if i + 1 < data_length:
            byte1 = data[i]
            byte2 = data[i + 1]
            checksum += (byte1 + (byte2 << 8))
        elif i < data_length:
            checksum += data[i]

    checksum += (checksum >> 16)
    checksum = ~checksum & 0xffff

    return checksum


class NetworkScanner:
    def __init__(self, network, timeout_ms):
        self.network = network
        # Timeout in milliseconds
        self.timeout = timeout_ms
        self.active_hosts = []
        self.lock = threading.Lock()

    def create_socket(self) -> socket.socket:
        """Creates a raw socket"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            return s
        except socket.error as e:
            print(f"Socket creation error: {e}")
            sys.exit()

    def create_packet(self, dst_ip) -> tuple[bytes, bytes]:
        """
            Creates a packet with IP and ICMP headers

            :param dst_ip: Destination IP address
            :return: Packet with IP Header and Packet ICMP Header
        """
        # Criar cabeçalho IP
        self_ip = socket.gethostbyname(socket.gethostname())
        ip = IP(self_ip, dst_ip)
        
        # Criar pacote ICMP
        icmp = ICMP()
    
        # Pack IP header
        ip_header = struct.pack("!BBHHHBBH4s4s", 
            (ip.version << 4) + ip.ihl, ip.tos, ip.tot_len,
            ip.id, ip.frag_off, ip.ttl, ip.protocol, ip.check,
            ip.saddr, ip.daddr)
        
        # Pack ICMP header
        icmp_packet = struct.pack("!BBHHH", 
            icmp.type, icmp.code, icmp.checksum,
            icmp.id, icmp.sequence)
        
        # Calcular checksum
        icmp_checksum = calculate_checksum(icmp_packet)
        
        # Remontar pacote ICMP com checksum
        icmp_packet = struct.pack("!BBHHH",
            icmp.type, icmp.code, icmp_checksum,
            icmp.id, icmp.sequence)
        
        return ip_header, icmp_packet

    def scan_host(self, ip) -> None:
        """
            Sends an ICMP echo request to a given IP address

            :param ip: IP address to send the ICMP echo request
        """
        sock = self.create_socket()
        _ip_header, icmp_packet = self.create_packet(ip)
        
        start_time = time.time()
        sock.sendto(icmp_packet, (ip, 0))
        
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
        """Scans the network for active hosts"""
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
        program_name = sys.argv[0]
        print(f"Uso: python {program_name} <rede/mascara> <timeout_ms>")
        print(f"Exemplo: python {program_name} 192.168.15.0/24 1000")
        sys.exit(1)

    network = sys.argv[1]
    timeout = int(sys.argv[2])

    scanner = NetworkScanner(network, timeout)
    scanner.scan()


if __name__ == "__main__":
    main()