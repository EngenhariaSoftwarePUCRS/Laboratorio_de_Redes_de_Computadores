import socket
import sys
import time
from struct import pack


def checksum(msg):
	s = 0
	
	# loop taking 2 characters at a time
	for i in range(0, len(msg), 2):
		w = msg[i] + (msg[i+1] << 8 )
		s = s + w
	
	s = (s>>16) + (s & 0xffff)
	s = s + (s >> 16)
	
	#complement and mask to 4 byte short
	s = ~s & 0xffff
	
	return s


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error as msg:
        print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    
    packet = ''
    
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

    # TCP Header fields
    tcp_source = 12345 # source port
    tcp_dest = 80 # destination port
    tcp_seq = 454
    tcp_ack_seq = 0
    tcp_doff = 5 #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags
    tcp_fin = 0
    tcp_syn = 1
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0
    tcp_window = socket.htons(5840) # maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)

    user_data = b'Hello, how are you'

    # pseudo header fields
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length)
    psh = psh + tcp_header + user_data

    tcp_check = checksum(psh)

    # make the tcp header again and fill the correct checksum
    tcp_header = pack('!HHLLBBH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H', tcp_check) + pack('!H', tcp_urg_ptr)

    # final full packet - syn packets dont have any data
    packet = ip_header + tcp_header + user_data

    # increase count to send more packets
    count = 3

    for i in range(count):
        print('Sending packet no ' + str(i))
        # Uncomment for flooding
        # while True:
        s.sendto(packet, (dest_ip, 0))
        time.sleep(1)
    
    print('Packet sent successfully')


if __name__ == '__main__':
    # Based on https://www.binarytides.com/raw-socket-programming-in-python-linux/
    main()
