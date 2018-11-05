import sys
import getopt
import socket
import threading
import time
import numpy as np
import struct
import os

ICMP_ECHO_REQUEST = 8


def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = ord(str[count+1]) * 256 + ord(str[count])
        csum = csum + thisVal
        csum = csum & 0xffffffffL
        count = count + 2
    if countTo < len(str):
        csum = csum + ord(str[len(str) - 1])
        csum = csum & 0xffffffffL
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def ping(dest, timeout, packet_id, sequence_num, payload):
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    except socket.error as e:
        print("cannot establish socket")
        return
    sock.setblocking(0)
    check_sum = 0
    dummy_header = struct.pack(
        'bbHHh', ICMP_ECHO_REQUEST, 0, check_sum, packet_id, sequence_num
    )
    payload_d = struct.pack('p', payload)
    check_sum = socket.htons(checksum(dummy_header + payload_d))
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
                         check_sum, packet_id, sequence_num)
    packet = header + payload_d

    # AF_INET address must be tuple, not str
    start_time = time.time()
    start_time = 0
    while packet:
        try:
            start_time = time.time()
            size = sock.sendto(packet, (dest, 1))
        except:
            print("Failed to send the packet")
        packet = packet[size:]

    data = ''
    while True:
        if time.time() - start_time >= timeout:
            return -1
        # non-blocking as it is set as non-blocking previously
        try:
            data, addr = sock.recvfrom(1024)
            break
        except:
            # when it doesn't receive data immediately
            pass
    recv_time = time.time()
    (version, c_type, length,id, flags, ttl, protocol, check__sum, src_ip, dest_ip) = struct.unpack('!BBHHHBBHII', data[0:20])
    (res_type, res_code, res_checksum, res_id, res_seq) = struct.unpack(
        'bbHHh', data[20:28])
    if not(res_type == 0 and res_code == 0):
        print("Error...Packet received with ICMP type %d code %d \n",
              res_type, res_code)
    if not res_id == packet_id:
        print(
            "Error...Packet received with packetId %d, supposed to be %d \n", res_id, packet_id)
    else:
        print("Reply from {}: bytes={}, time={}ms, TTL={}").format(dest, len(payload), (recv_time - start_time) * 1000 // 1, ttl)
        return recv_time - start_time


def main(argv):
    # variale declarations
    payload = 'hello'
    count = 1
    dest = '8.8.8.8'

    # get command line options
    try:
        myopts, args = getopt.getopt(argv, "d:p:c:l:")
    except getopt.GetoptError as e:
        print(str(e))
        print("Options not correct. Usage: -d -p -c -l")
        sys.exit(2)

    if not myopts:
        print("Options not correct. Usage: -d -p -c -l")
        sys.exit(2)

    for k, v in myopts:
        if k == '-p':
            payload = v
        elif k == '-d':
            dest = v
        elif k == '-c':
            count = int(v)

    sent = 0
    timeout = 1

    rtts = []
    packet_id = np.random.choice(range(count), replace=False)
    minRtt = 1
    maxRtt = 0
    print("Pinging {} with {} bytes of data \"{}\"".format(
        dest, len(payload), payload))

    for i in range(count):
        rtt = ping(dest, timeout, packet_id, 1, payload)
        if (rtt != -1):
            rtts.append(rtt)
            if rtt < minRtt:
                minRtt = rtt
            if rtt > maxRtt:
                maxRtt = rtt
        time.sleep(timeout - rtt if timeout - rtt > 0 else 0)
    averageRtt = sum(rtts) / len(rtts)
    print("Ping statistics for {}:".format(dest))
    print("Packets: Sent={}, Received={}, Lost={}({}% loss)".format(count, len(rtts), count - len(rtts), (count-len(rtts))/count))
    print("Approximate round trip times in milli-seconds:")
    print("Minimum = {}ms,  Maximum = {}ms, Average={}ms".format(minRtt * 1000 // 1,maxRtt * 1000 // 1,averageRtt * 1000 // 1))

if __name__ == "__main__":
    main(sys.argv[1:])
