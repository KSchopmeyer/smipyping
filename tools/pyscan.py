#! /usr/bin/python
# pyscan.py - Python based SYN scanner.  A SYN packet is sent through a raw socket.
# If a SYN/ACK is received, the Linux TCP stack sends a RST/ACK, and an open
# port is assumed.  Otherwise, a closed or filtered port is assumed.
# Does not rely on scapy, rather creates its own packets and raw sockets.
# Must be run as root.
#
# Thanks to Silver Moon for some example code in his post "Syn flood and
# raw sockets at http://www.binarytides.com/python-syn-flood-program-raw-sockets
#
import socket, sys, random
from struct import *
 
# checksum functions - direct from Silver Moon
def checksum(msg):
    s = 0
    #loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = (ord(msg[i]) <<8) + (ord(msg[i+1]) )
        s = s + w
 
    s = (s>>16) + (s & 0xffff);
    # complement and mask to 4 byte short
    s = ~s & 0xffff
    return s
 
 
def create_socket(source_ip,dest_ip):
    #create a raw socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error , msg:
        print 'Socket could not be created.  Error: ',str(msg[0]),' Message: ',msg[1]
        sys.exit()
 
    #tell kernel not to put in headers since we are providing it
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    return s
 
def create_ip_header(source_ip, dest_ip):
    packet = ''
 
    # ip header fields
    headerlen = 5
    version = 4
    tos = 0
    tot_len = 20 + 20
    id = random.randrange(18000,65535,1)
    frag_off = 0
    ttl = 255
    protocol = socket.IPPROTO_TCP
    check = 10
    saddr = socket.inet_aton ( source_ip )
    daddr = socket.inet_aton ( dest_ip )
    hl_version = (version << 4) + headerlen
    ip_header = pack('!BBHHHBBH4s4s', hl_version, tos, tot_len, id, frag_off, ttl, protocol, check, saddr, daddr)
    return ip_header
''' create_ip_header '''
 
def create_tcp_syn_header(source_ip, dest_ip, dest_port):
    # tcp header fields
    source = random.randrange(32000,62000,1)    # source port
    seq = 0
    ack_seq = 0
    doff = 5
    # tcp flags
    fin = 0
    syn = 1
    rst = 0
    psh = 0
    ack = 0
    urg = 0
    window = socket.htons (8192)    # maximum window size
    check = 0
    urg_ptr = 0
    offset_res = (doff << 4) + 0
    tcp_flags = fin + (syn<<1) + (rst<<2) + (psh<<3) + (ack<<4) + (urg<<5)
    tcp_header = pack('!HHLLBBHHH', source, dest_port, seq, ack_seq, offset_res, tcp_flags, window, check, urg_ptr)
    #pseudo header fields
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton( dest_ip )
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)
    psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length);
    psh = psh + tcp_header;
    tcp_checksum = checksum(psh)
 
    #make the tcp header again and fill in the correct checksum
    tcp_header = pack('!HHLLBBHHH', source, dest_port, seq, ack_seq, offset_res, tcp_flags, window, tcp_checksum, urg_ptr)
    return tcp_header
''' create_tcp_syn_header ends '''
 
def range_scan(source_ip, dest_ip, start_port, end_port) :
    syn_ack_received = []   # store the list of open ports here
    # final full packet - syn packets don't have any data
    for j in range (start_port, end_port) :
        s = create_socket(source_ip, dest_ip)
        ip_header = create_ip_header(source_ip, dest_ip)
        tcp_header = create_tcp_syn_header(source_ip, dest_ip,j)
        packet = ip_header + tcp_header
        s.sendto(packet, (dest_ip, 0))
        data = s.recvfrom(1024) [0][0:]
        ip_header_len = (ord(data[0]) & 0x0f) * 4
        ip_header_ret = data[0: ip_header_len - 1]
        tcp_header_len = (ord(data[32]) & 0xf0)>>2
        tcp_header_ret = data[ip_header_len:ip_header_len+tcp_header_len - 1]
        if ord(tcp_header_ret[13]) == 0x12: # SYN/ACK flags set
            syn_ack_received.append(j)
    return syn_ack_received
''' range_scan ends '''

# Here's the program stub to test the code:
open_port_list = []
ipsource = '10.1.134.33'
ipdest = '10.1.134.33'
start = 100
stop = 450
step = (stop-start)/10
scan_ports = range(start, stop, step)
if scan_ports[len(scan_ports)-1] < stop:
    scan_ports.append(stop)
for i in range(len(scan_ports)-1):
    opl = range_scan(ipsource, ipdest, scan_ports[i], scan_ports[i+1])
    open_port_list.append(opl)
for i in range(len(open_port_list)):
    print 'Process #: ',i,' Open ports: ',open_port_list[i]
print 'A list of all open ports found: '
for i in range(len(open_port_list)):
    for j in range(len(open_port_list[i])):
        print open_port_list[i][j],', '


