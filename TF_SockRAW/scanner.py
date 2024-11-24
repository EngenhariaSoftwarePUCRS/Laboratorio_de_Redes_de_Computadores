import socket
import struct
import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor

def calculate_checksum(packet):
    """Calcula o checksum do cabeçalho ICMP."""
    if len(packet) % 2 == 1:
        packet += b'\x00'
    checksum = sum(struct.unpack("!%dH" % (len(packet) // 2), packet))
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    return ~checksum & 0xffff

def create_icmp_packet(identifier, sequence_number):
    """Cria um pacote ICMP Echo Request."""
    icmp_type = 8  # Echo Request
    icmp_code = 0
    checksum = 0  # Será recalculado
    header = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, identifier, sequence_number)
    data = b'PingScan'  # Dados arbitrários
    checksum = calculate_checksum(header + data)
    header = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, identifier, sequence_number)
    return header + data

def ping_host(ip, timeout):
    """Envia um pacote ICMP e aguarda uma resposta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.settimeout(timeout / 1000)
            packet = create_icmp_packet(identifier=1, sequence_number=1)
            sock.sendto(packet, (ip, 0))
            start_time = time.time()
            sock.recv(1024)  # Recebe resposta
            return ip, (time.time() - start_time) * 1000
    except socket.timeout:
        return ip, None
    except Exception as e:
        print(f"Erro ao pingar {ip}: {e}")
        return ip, None

def scan_network(network_cidr, timeout):
    """Realiza a varredura de todos os hosts ativos em uma rede."""
    network = ipaddress.ip_network(network_cidr, strict=False)
    hosts = list(network.hosts())  # Ignora endereço de rede e broadcast
    active_hosts = []

    print(f"Iniciando varredura na rede {network_cidr}...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(lambda ip: ping_host(str(ip), timeout), hosts)

    for ip, response_time in results:
        if response_time is not None:
            active_hosts.append((ip, response_time))

    total_time = time.time() - start_time
    print(f"Varredura concluída em {total_time:.2f} segundos.")
    print(f"Máquinas ativas: {len(active_hosts)}")
    for host, response_time in active_hosts:
        print(f"{host} - Tempo de resposta: {response_time:.2f} ms")

    return active_hosts

# Teste
if __name__ == "__main__":
    scan_network("192.168.15.4/24", timeout=1000)
