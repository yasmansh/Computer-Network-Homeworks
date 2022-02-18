import socket, threading, time

host = '127.0.0.1'
ports = [8010, 8020, 8030]
ids = [1, 2, 3]

# id: [server, client, leader_id, id_lock]
nodes = {}
leader = -1
election_lock = threading.Lock()


# creating server and client for a peer
def create_node(s_port: int, n_id: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, s_port))
    server.listen(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    id_lock = threading.Lock()
    nodes[n_id] = [server, client, n_id, id_lock]
    server_thread = threading.Thread(target=run_as_server, args=(server, ids.index(n_id)))
    server_thread.start()
    pass


def read(node: list):
    global leader
    client = node[1]
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            lock = node[3]
            if message == 'id':
                while lock.locked():
                    pass
                lock.acquire()
                client.send(f"{node[2]}".encode('ascii'))
            else:
                leader = message
                print(f"Leader is {message}")
        except:
            client.close()
            break


def run_as_client(node: list, port: int):
    client = node[1]
    client.connect((host, port))

    read_thread = threading.Thread(target=read, args=(node,))
    read_thread.start()
    print(f"Client {node[2]} is now up.")


def handle(client: socket.socket, s_index: int):
    while election_lock.locked():
        pass
    client.send('id'.encode('ascii'))
    server_id = ids[s_index]
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            client_id = int(message)
            lock = nodes[server_id][3]
            while not lock.locked():
                pass
            if leader != -1:
                break
            print(f"Client sent {client_id} to server {server_id}, id: {nodes[server_id][2]}")
            if client_id > nodes[server_id][2]:
                nodes[server_id][2] = client_id
                print(f"Update in server {server_id}")
                next_message = 'id'
            elif client_id < nodes[server_id][2]:
                next_message = 'id'
            else:
                next_message = client_id
            client.send(f"{next_message}".encode('ascii'))
            lock.release()
        except:
            break


def run_as_server(server: socket.socket, s_index: int):
    print(f"Server {s_index} is now up.")
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle, args=(client, s_index))
        thread.start()


for i in range(0, 3):
    create_node(ports[i], ids[i])

election_lock.acquire()
for i in range(0, 3):
    run_as_client(nodes[ids[i]], ports[(i + 1) % 3])

print("Starting the process")
time.sleep(5)
election_lock.release()
