import socket
import os
import hashlib

serverAddress = "localhost"
serverPort = 4545

splitted_by = "|__YaSaMaN.SH__|"
f = open("getip_", "r")
serverAddress = f.read().rstrip()
f.close()

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(6)
    server_address = (serverAddress, serverPort)
    dir = os.path.dirname(__file__)
    input_ = raw_input("Your file:")
    print(server_address)
    message = input_ + dir
    sequence_number_flag = 0
    file = open("_" + input_, 'w')

    try:
        connection_counter = 0
        sent = sock.sendto(message, server_address)
        while True:
            try:
                data, server = sock.recvfrom(4096)
                connection_counter = 0
            except:
                connection_counter += 1
                if connection_counter < 6:
                    print("Connection timeout\n")
                    continue
                else:
                    print("skipping request\n")
                    os.remove("_" + input_)
                    break
            sequence_number = data.split(splitted_by)[1]
            client_hash_code = hashlib.sha1(data.split(splitted_by)[3]).hexdigest()
            server_hash_code = data.split(splitted_by)[0]
            print("Server: %s on port %s" % server)
            if server_hash_code == client_hash_code and sequence_number_flag == int(sequence_number == True):
                packet_length = data.split(splitted_by)[2]
                if data.split(splitted_by)[3] == "NOTFOUND-ERR":
                    print("File not found on the server!")
                    os.remove("_" + input_)
                else:
                    file.write(data.split(splitted_by)[3])

                sent = sock.sendto(str(sequence_number) + "," + packet_length, server)
            else:
                print("Checksums are different")
                continue
            if int(packet_length) < 500:
                sequence_number = int(not sequence_number)
                break

    except:
	pass
    finally:
        sock.close()
        file.close()
