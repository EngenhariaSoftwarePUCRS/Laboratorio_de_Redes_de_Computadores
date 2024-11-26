import socket
import struct
import sys
import time
from datetime import datetime

from print import print_, print_error


output_file: str
interface: str
history: list[dict[str, str]] = []
dns_cache: dict[str, str] = {}


def create_socket():
    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        sock.bind((interface, 0))
        return sock
    
    except socket.error as e:
        print_error(f"Erro ao criar socket: {e}")
        sys.exit(1)


def parse_ethernet_header(packet):
    eth_length = 14
    eth_header = packet[:eth_length]
    eth = struct.unpack('!6s6sH', eth_header)

    return eth[2], packet[eth_length:]


def parse_ip_header(packet):
    ip_header = packet[:20]
    iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
    
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])
    
    return protocol, s_addr, d_addr, packet[iph_length:]


def parse_tcp_header(packet):
    tcp_header = packet[:20]
    tcph = struct.unpack('!HHLLBBHHH', tcp_header)
    
    source_port, dest_port, sequence, _acknowledgement, doff_reserved = tcph[:5]
    # Data offset (doff) indica o tamanho do cabeçalho TCP em palavras de 32 bits
    tcph_length = doff_reserved >> 4
    
    return source_port, dest_port, packet[tcph_length*4:]


def parse_udp_header(packet):
    udph_length = 8
    udp_header = packet[:udph_length]
    udph = struct.unpack('!HHHH', udp_header)
    
    source_port, dest_port = udph[:2]
    
    return source_port, dest_port, packet[udph_length:]


def parse_dns_packet(data) -> tuple[str, str] | tuple[None, None]:
    """
    Parse DNS packet and return the domain and resolved IP

    :param data: DNS data
    :return: Domain and resolved IP
    """

    domain: str | None = None
    resolved_ip: str | None = None

    try:
        # Simplified DNS header
        dns_header = struct.unpack('!HHHHHH', data[:12])
        query_count = dns_header[2]
        answer_count = dns_header[3]
        
        # Skip DNS header
        offset = 12
        
        for _ in range(query_count):
            qname = []
            while data[offset] != 0:
                length = data[offset]
                offset += 1
                qname.append(data[offset:offset+length].decode())
                offset += length
            domain = '.'.join(qname)
            offset += 5

        for _ in range(answer_count):
            if data[offset] & 0xC0 == 0xC0:
                offset += 2
            else:
                while data[offset] != 0:
                    length = data[offset]
                    offset += 1 + length
                offset += 1

            rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', data[offset:offset+10])
            offset += 10

            # Type A, Class IN, IPv4
            if rtype == 1 and rclass == 1 and rdlength == 4:
                resolved_ip = socket.inet_ntoa(data[offset:offset + rdlength])
                offset += rdlength
                break

            offset += rdlength

        return domain, resolved_ip
            
    except Exception as e:
        print_error(f"Erro ao processar pacote DNS ({data}): {e}")
        return None


def parse_http_request(data) -> tuple[str | None, str | None]:
    """
    Parse HTTP request and return the URL path

    :param data: HTTP data
    :return: Host and URL path
    """
    host: str | None = None
    path: str | None = None

    try:
        http_data = data.decode('utf-8')
        lines = http_data.split('\n')

        http_rest_protocols = ['GET', 'POST']
        for line in lines:
            if any(line.startswith(protocol) for protocol in http_rest_protocols):
                _protocol, url_path, _http_version = line.split(' ')
                path = url_path
            if line.startswith('Host:'):
                host = line.split(' ')[1]
        
    except:
        pass

    return host, path


def save_history(start_time: str):
    print_("green", f"Salvando historico em {output_file}")
    with open(output_file, 'w') as f:
        f.write('<html>\n')
        f.write('<header>\n')
        f.write('<title>Historico de Navegacao</title>\n')
        f.write('</header>\n')
        f.write('<body>\n')
        f.write(f'<h1>Historico de Navegacao ({start_time})</h1>\n')
        f.write('<table border="1">\n')
        f.write('<tr>\n')
        f.write('<th>Timestamp</th>\n')
        f.write('<th>Source IP</th>\n')
        f.write('<th>Host IP</th>\n')
        f.write('<th>Protocol</th>\n')
        f.write('<th>Domain</th>\n')
        f.write('<th>URL Path</th>\n')
        f.write('</tr>\n')
        for entry in history:
            f.write('<tr>\n')
            f.write(f'<td>{entry["timestamp"]}</td>\n')
            f.write(f'<td>{entry["src_ip"]}</td>\n')
            f.write(f'<td>{entry["host_ip"]}</td>\n')
            f.write(f'<td>{entry["protocol"]}</td>\n')
            f.write(f'<td>{entry["domain"]}</td>\n')
            f.write(f'<td><a href="{entry["url"]}">{entry["url"]}</a></td>\n')
            f.write('</tr>\n')
        f.write('</tr>\n')
        f.write('</body>\n')
        f.write('</html>\n')


def start_sniffing(packet_limit: int | None = None, time_limit_s: int | None = None):
    """
    Start sniffing packets on the network

    :param packet_limit: Maximum number of packets to capture
    :param time_limit: Maximum time to capture packets in seconds
    """
    global dns_cache, history

    sock = create_socket()
    start_time = time.time()
    captured_packets = 0
    
    try:
        while True:
            if packet_limit is not None and captured_packets >= packet_limit:
                break

            if time_limit_s is not None and time.time() - start_time >= time_limit_s:
                break

            packet = sock.recvfrom(65535)[0]
            
            # Parse Ethernet
            eth_protocol, data = parse_ethernet_header(packet)
            
            # Ignore non-IP packets
            if eth_protocol != 0x0800:
                # print_("red", f"Non-IP Packet Detected (EtherType: {eth_protocol:#04x}). Skipping...")
                continue

            captured_packets += 1
            
            protocol, src_ip, dst_ip, data = parse_ip_header(data)
            protocol_mapper = {1: "ICMP", 6: "TCP", 17: "UDP"}
            protocol_name = protocol_mapper.get(protocol, f"Unknown ({protocol})")

            if protocol_name not in protocol_mapper.values():
                print_("cyan", f'[{captured_packets}] Protocol: {protocol_name} | IP Origem: {src_ip} -> IP Destino: {dst_ip}')
            
            # Processar DNS (UDP porta 53)
            if protocol_name == "UDP":
                src_port, dst_port, data = parse_udp_header(data)
                if src_port == 53 or dst_port == 53:  # DNS
                    domain, resolved_ip = parse_dns_packet(data)
                    if resolved_ip and domain and dst_ip not in dns_cache:
                        dns_cache[resolved_ip] = domain
                        print_("yellow", f"DNS cached: {resolved_ip} -> {domain}")
            
            # Processar HTTP (TCP porta 80)
            elif protocol_name == "TCP":
                src_port, dst_port, data = parse_tcp_header(data)
                http_type = "http" if dst_port == 80 else "https" if dst_port == 443 else None
                if http_type:
                    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
                    hostname = dns_cache.get(dst_ip, None)
                    if not hostname:
                        # Skip if no hostname is cached
                        print_("red", f"No DNS record for IP {dst_ip}")
                        continue
                    url = f"{http_type}://"
                    if http_type == "https":
                        url += hostname
                        host = hostname
                    elif http_type == "http":
                        host, url_path = parse_http_request(data)
                        if not host:
                            continue
                        url += host
                        if url_path:
                            url += url_path
                    url = url.replace('\r', '').replace('\n', '')
                    entry = {
                        "timestamp": timestamp,
                        "src_ip": src_ip,
                        "host_ip": dst_ip,
                        "protocol": http_type,
                        "domain": host,
                        "url": url,
                    }
                    history.append(entry)
            
    except KeyboardInterrupt:
        print_("yellow", "\nEncerrando...")
    
    finally:
        print_("green", f"\nEncerrado. Capturados {captured_packets} pacotes.")
        save_history(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        # Write dns_cache to file
        with open("output/dns_cache.txt", "w") as f:
            for ip, domain in dns_cache.items():
                f.write(f"{ip} {domain}\n")
        sock.close()


def main():
    if len(sys.argv) < 2:
        program_name = sys.argv[0]
        print_("magenta", f"Uso: python {program_name} [interface=eth0] [packet_limit=None] [time_limit_s=None] [output_file=output/history.html]")
        print_("magenta", f"Exemplo: python3 {program_name} eth0 100 10 output/history.html")

    global interface, output_file
    interface = sys.argv[1] if len(sys.argv) > 1 else "eth0"
    output_file = sys.argv[4] if len(sys.argv) > 4 else "output/history.html"

    packet_limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    time_limit_s = int(sys.argv[3]) if len(sys.argv) > 3 else None

    start_sniffing(packet_limit, time_limit_s)


if __name__ == "__main__":
    main()
