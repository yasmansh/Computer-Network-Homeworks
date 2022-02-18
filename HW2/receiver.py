import socket
import threading
import time
import datetime
import hashlib
import os

serverAddress = "localhost"
serverPort = 4545

sequence_number_flag = 0
splitted_by = "|__YaSaMaN.SH__|"


class packet():
    sequence_number = 0
    data = 0
    length_of_data = 0
    checksum = 0

    def set(self, data):
        self.data = data
        self.length_of_data = str(len(data))
        self.checksum = hashlib.sha1(data).hexdigest()


def handler(address, data):
    packet_counter = 0
    time.sleep(0.6)
    start = time.time()
    packet_ = packet()
    thread_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        try:
            print("Opening file %s" % data)
            file = open(data, 'r')
            data = file.read()
            file.close()
        except:
            packet_.set("NOTFOUND-ERR")
            reply_packet = str(packet_.checksum) + splitted_by + str(packet_.sequence_number) + splitted_by + str(
                packet_.length_of_data) + splitted_by + packet_.data
            thread_sock.sendto(reply_packet, address)
            print("File not found!\n")
            return

        window_size = 500
        i = 0
        while i <= (len(data) / window_size):
            packet_counter += 1
            message = data[i * window_size:i * window_size + window_size]
            packet_.set(message)
            reply_packet = str(packet_.checksum) + splitted_by + str(packet_.sequence_number) + splitted_by + str(
                packet_.length_of_data) + splitted_by + packet_.data
            thread_sock.sendto(reply_packet, address)
            thread_sock.settimeout(5)  # waiting for ack
            try:
                ack, address = thread_sock.recvfrom(100)
            except:
                print("Timeout and Retransmission\n")
                continue
            if ack.split(",")[0] == str(packet_.sequence_number):
                packet_.sequence_number = int(not packet_.sequence_number)
                i += 1
    except:
        print("Error\n")


# UDP-Based connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Server
f = open("getip_", "w")
os.system("ifconfig -a  | head -2 | cut -c 14-21 | tail -1 | tail -1 > getip_")
f.close()
f = open("getip_", "r")
serverAddress = f.read().rstrip()
f.close()
server_address = (serverAddress, serverPort)
print("Address %s Port %s" % server_address)
sock.bind(server_address)

while True:
   # print("Waiting to receive file\n")  # Listening
    data, address = sock.recvfrom(600)
    connectionThread = threading.Thread(target=handler, args=(address, data))
    connectionThread.start()
    print("Received from " + str(address))
