import socket
from struct import pack
import sys

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    
    source_ip = '192.168.1.101'
    dest_ip = '192.168.1.1'	# or socket.gethostbyname('www.google.com')

    # IP Header fields
    ip_ihl = 5 # Internet Header Length
    ip_ver = 4 # Version
    ip_tos = 0 # Type of Service
    ip_tot_len = 0 # kernel will fill the correct total length
    ip_id = 54321 #Id of this packet
    ip_frag_off = 0 # Fragmentation offset
    ip_ttl = 255 # Time to live
    ip_proto = socket.IPPROTO_TCP # Protocol
    ip_check = 0 # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton(source_ip) #Spoof the source ip address if you want to
    ip_daddr = socket.inet_aton(dest_ip) # Destination IP

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

    print('IP Header: ', ip_header)


if __name__ == '__main__':
    # Based on https://www.binarytides.com/raw-socket-programming-in-python-linux/
    main()
