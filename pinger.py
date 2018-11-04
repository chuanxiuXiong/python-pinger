import sys
import getopt
import socket
import threading
import time
import numpy as np
import struct
import os

ICMP_ECHO_REQUEST = 8


def checksum(source_string):
    temp_sum = 0
    count_to = (len(source_string) / 2) * 2
    count = 0
    while count < count_to:
        this_val = ord(source_string[count + 1])*256+ord(source_string[count])
        temp_sum = temp_sum + this_val
        temp_sum = temp_sum & 0xffffffff  # Necessary?
        count = count + 2
    if count_to < len(source_string):
        temp_sum = temp_sum + ord(source_string[len(source_string) - 1])
        temp_sum = temp_sum & 0xffffffff  # Necessary?
    temp_sum = (temp_sum >> 16) + (temp_sum & 0xffff)
    temp_sum = temp_sum + (temp_sum >> 16)
    answer = ~temp_sum
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
    # process_id = os.getpid() & 0xFFFF
    check_sum = 0
    dummy_header = struct.pack(
        'bbHHh', ICMP_ECHO_REQUEST, 0, check_sum, packet_id, sequence_num
    )
    check_sum = socket.htons(checksum(payload + dummy_header))
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
                         check_sum, packet_id, sequence_num)
    start_time = time.time()
    packet = header + payload
    print("Pinging {} with {} bytes of data {}".format(
        dest, len(payload), payload))
    start_time = 0
    while packet:
        try:
            start_time = time.time()
            size = sock.sendto(header + payload, (dest, 1))
        except:
            print("Failed to send the packet")
        packet = packet[size:]

    print("Finished socket")

    data = ''
    while True:
        if time.time() - start_time >= timeout:
            return -1
        # non-blocking as it is set as non-blocking previously
        try:
            data, _ = sock.recvfrom(1024)
            break
        except:
            # when it doesn't receive data immediately
            continue
    recv_time = time.time()
    received_header = data[0:20]
    (res_type, res_code, res_checksum, res_id, res_seq) = struct.unpack(
        'bbHHh', data[20:28])
    print("res_type {}\n res_code {}\n res_checksum {}\n res_id {}\n res_seq{}".format(
        res_type, res_code, res_checksum, res_id, res_seq))
    if not(res_type == 0 and res_code == 0):
        print("Error...Packet received with ICMP type %d code %d \n",
              res_type, res_code)
    if not res_id == packet_id:
        print(
            "Error...Packet received with packetId %d, supposed to be %d \n", res_id, packet_id)
    else:
        # res_time = struct.unpack('d', data[28:36])
        return recv_time - start_time


def main(argv):
    # variale declarations
    payload = ''
    count = 0
    dest = ''

    # get command line options
    try:
        myopts, args = getopt.getopt(argv, "d:p:c:")
    except getopt.GetoptError as e:
        print(str(e))
        print("Usage: %s -s serverIP -p portno -l logfile -n name" %
              sys.argv[0])
        sys.exit(2)

    if not myopts:
        print("Usage: %s -s serverIP -p portno -l logfile -n name" %
              sys.argv[0])
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
    for _ in range(count):
        rtt = ping(dest, timeout, packet_id, 1, payload)
        rtts.append(rtt)
        time.sleep(timeout - rtt if timeout - rtt > 0 else 0)
        print("printing the rtts")
        print(rtt)


if __name__ == "__main__":
    main(sys.argv[1:])
