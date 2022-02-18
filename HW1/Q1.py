import socket, threading, time

host = '127.0.0.1'
ports = []
ids = []

# node: [server, clients, n_id, is_avaliable, counter]
nodes = {}
election_lock = threading.Lock()
leader = -1
found = False


# creating server and client for a p2p connection
def create_node(s_port: int, n_id: int, n: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, s_port))
    server.listen(n)
    clients = []
    for i in range(n):
        clients.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    nodes[n_id] = [server, clients, n_id, 1, 0]
    server_thread = threading.Thread(target=run_as_server, args=(server, ids.index(n_id)))
    server_thread.start()
    pass


def read(node: list):
    client = node[1][node[4] - 1]
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'Are you available?':
                if node[3] == 1:
                    client.send(f"I am available.{node[2]}".encode('ascii'))
                else:
                    client.send("I am busy.".encode('ascii'))
        except:
            client.close()
            break


def run_as_client(node: list, port: int):
    client = node[1][node[4]]
    node[4] += 1
    client.connect((host, port))

    read_thread = threading.Thread(target=read, args=(node,))
    read_thread.start()
    read_thread.close()


def handle(client: socket.socket, s_index: int):
    global leader
    global found
    while election_lock.locked():
        pass
    client.send('Are you available?'.encode('ascii'))
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message.__contains__('I am available.'):
                client_id = int(message[15:])
                print(f"Client {client_id} is available.")
                leader = max(leader, client_id)
                found = True
                time.sleep(1)
        except:
            break


def run_as_server(server: socket.socket, s_index: int):
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle, args=(client, s_index))
        thread.start()


n = int(input())
ids = [int(x) for x in input().split()]

for i in range(n):
    ports.append(4500 + i * 5)
    create_node(ports[i], ids[i], n)

election_lock.acquire()
from_ = 0
while (True):

    command = input()

    if command == 'Find Leader':
        if nodes[ids[from_]][3] == 0:
            while nodes[ids[from_]][3] == 0:
                from_ += 1
            print(f"Client {ids[from_]} is available.")

        leader = ids[from_]
        for i in range(n):
            if ids[i] > ids[from_]:
                try:
                    run_as_client(nodes[ids[i]], ports[from_])
                except:
                    pass

        time.sleep(5)
        if election_lock.locked():
            election_lock.release()
            time.sleep(5)
        if not found:
            print(f"Client {ids[from_]} is leader.")
        else:
            print(f"Client {leader} is leader.")
    elif command.__contains__('is busy.'):
        busy_id = int(command[7:-9])
        nodes[busy_id][3] = 0

