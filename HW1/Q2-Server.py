import socket, threading, time
import random

host = '127.0.0.1'
port = 8072

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(7)
print("Waiting for other players...")
clients = []
roles = []
names = []
is_alive = []

def handle(client: socket.socket):
    # Introduction
    while True:
        if len(clients) == 7:
            for i in range(7):
                msg = clients[i].recv(1024).decode('ascii')
                names.append(msg)
                is_alive.append(True)
            print('Names:\t' + str(names))
            print("Start Game")
            ravi_index = random.randint(1, 6)
            clients[ravi_index].sendall("Your role: ravi".encode('ascii'))
            msg = clients[ravi_index].recv(1024).decode('ascii')
            while msg != 'set roles':
                msg = clients[ravi_index].recv(1024).decode('ascii')
            shahrvand_team_id = ""
            if msg == 'set roles':
                r = ['mafia-pedar khaande', 'mafia-sade', 'shahrvand1', 'shahrvand2', 'karagah', 'pezeshk']

                for i in range(0, 7):
                    if i == ravi_index:
                        roles.append('ravi')
                    else:
                        random_role = random.choice(r)
                        roles.append(random_role)
                        clients[i].sendall(("Your role: " + random_role + "-Your ID: " + str(i + 1)).encode('ascii'))
                        r.remove(random_role)
                        if random_role in {'shahrvand1', 'shahrvand2', 'karagah', 'pezeshk'}:
                            shahrvand_team_id += (str(i + 1) + ' ')
                print('Roles:\t' + str(roles))
                clients[roles.index('mafia-pedar khaande')].sendall(shahrvand_team_id.encode('ascii'))
                msg = shahrvand_team_id + "gadfather:" + str(1 + roles.index('mafia-pedar khaande'))
                clients[roles.index('mafia-sade')].sendall(msg.encode('ascii'))

                clients[ravi_index].sendall(('Roles:' + str(roles)).encode('ascii'))
                msg = clients[ravi_index].recv(1024).decode('ascii')
                if msg == 'next state':
                    phase = 1
                    for c in clients:  # Night
                        c.sendall('phase1'.encode('ascii'))
            break
    shahrvandan_ids = []
    mafia_ids = []
    died_ids = []
    end_game = False
    for i in range(7):
        if roles[i] in {'mafia-pedar khaande', 'mafia-sade'}:
            mafia_ids.append(i)
        elif roles[i] in {'shahrvand1', 'shahrvand2', 'karagah', 'pezeshk'}:
            shahrvandan_ids.append(i)

    phase = 1  # Night
    save_doctor = False
    while not end_game:

        if phase == 1:  # Night

            if is_alive[roles.index('mafia-sade')] and is_alive[roles.index('mafia-pedar khaande')]:
                msg = clients[roles.index('mafia-sade')].recv(1024).decode('ascii')
                clients[roles.index('mafia-pedar khaande')].sendall(('mafia offers:' + msg[6]).encode('ascii'))
                for d_id in died_ids:
                    clients[d_id].sendall(("Mafia offered " + str(roles[int(msg[6]) - 1]) + " to godfather.").encode(
                        'ascii'))
                clients[ravi_index].sendall(("Mafia offered " + str(roles[int(msg[6]) - 1]) + " to godfather.").encode(
                    'ascii'))

            #
            if is_alive[roles.index('mafia-pedar khaande')]:
                msg = clients[roles.index('mafia-pedar khaande')].recv(1024).decode('ascii')
                selected_by_mafia = int(msg[7]) - 1
                for d_id in died_ids:
                    clients[d_id].sendall(("Mafia selected " + roles[selected_by_mafia] + ".").encode('ascii'))
                clients[ravi_index].sendall(("Mafia selected " + roles[selected_by_mafia] + ".").encode('ascii'))

            #
            elif is_alive[roles.index('mafia-sade')]:
                msg = clients[roles.index('mafia-sade')].recv(1024).decode('ascii')
                selected_by_mafia = int(msg[7]) - 1
                for d_id in died_ids:
                    clients[d_id].sendall(("Mafia selected " + roles[selected_by_mafia] + ".").encode('ascii'))

                clients[ravi_index].sendall(("Mafia selected " + roles[selected_by_mafia] + ".").encode('ascii'))

            #
            if is_alive[roles.index('pezeshk')]:
                msg = clients[roles.index('pezeshk')].recv(1024).decode('ascii')
                if save_doctor and (int(msg[7]) - 1) == roles.index('pezeshk'):
                    clients[roles.index('pezeshk')].sendall("Enter another id:".encode('ascii'))
                    msg = clients[roles.index('pezeshk')].recv(1024).decode('ascii')
                    selected_by_doctor = int(msg[0]) - 1
                else:
                    selected_by_doctor = int(msg[7]) - 1
                    if selected_by_doctor == roles.index('pezeshk'):
                        save_doctor = True
                for d_id in died_ids:
                    clients[d_id].d(("Pezeshk saved " + roles[selected_by_doctor] + ".").encode('ascii'))
                clients[ravi_index].sendall(("Pezeshk saved " + roles[selected_by_doctor] + ".").encode('ascii'))

            # estelam
            if is_alive[roles.index('karagah')]:
                msg = clients[roles.index('karagah')].recv(1024).decode('ascii')
                index = int(msg[7]) - 1
                if roles[index] == 'ravi':
                    clients[roles.index('karagah')].sendall(('ravi').encode('ascii'))
                elif roles[index] == 'mafia-sade':
                    clients[roles.index('karagah')].sendall(('mafia').encode('ascii'))
                else:
                    clients[roles.index('karagah')].sendall(('shahrvand').encode('ascii'))

                for d_id in died_ids:
                    clients[d_id].sendall(("Karagah selected " + roles[selected_by_mafia] + ".").encode('ascii'))
                clients[roles.index('ravi')].sendall(
                    ("Karagah selected " + roles[selected_by_mafia] + ".").encode('ascii'))

            ##

            clients[roles.index('ravi')].sendall('|'.encode('ascii'))

            msg = clients[ravi_index].recv(1024).decode('ascii')

            flag_kill = False
            if selected_by_doctor != selected_by_mafia:  # kill
                shahrvandan_ids.remove(selected_by_mafia)
                is_alive[selected_by_mafia] = False
                clients[selected_by_mafia].sendall(('You were killed.phase2').encode('ascii'))
                for d_id in died_ids:
                    clients[d_id].sendall(("GodFather killed " + roles[selected_by_mafia] + ".\nDay\n").encode('ascii'))

                died_ids.append(selected_by_mafia)

                flag_kill = True
                msg = names[selected_by_mafia] + ' is removed. -shahrvand'
                if len(shahrvandan_ids) == len(mafia_ids):
                    for c in clients:
                        c.sendall("The Mafia won.".encode('ascii'))
                    end_game = True
                    break
            phase = 2

            if flag_kill:
                msg = msg + 'phase2'
            else:
                msg = 'phase2'
            for i in range(7):
                if i in shahrvandan_ids or i in mafia_ids or roles[i] == 'ravi':
                    clients[i].sendall(msg.encode('ascii'))

        if phase == 2:  # Day
            pm = ''
            for i in range(7):
                if roles[i] != 'ravi' and is_alive[i]:
                    time.sleep(1)
                    msg = clients[i].recv(1024).decode('ascii')
                    if msg.__contains__('say'):
                        pm += names[i] + ' said ' + msg[4:] + '\n'

            print('after chat' + pm)
            for c in clients:
                c.sendall(pm.encode('ascii'))

            msg = clients[ravi_index].recv(1024).decode('ascii')
            if msg == 'next state':
                phase = 3
                for d_id in died_ids:
                    clients[d_id].sendall("Voting...\n".encode('ascii'))

                for i in range(7):
                    if i in shahrvandan_ids or i in mafia_ids or roles[i] == 'ravi':
                        clients[i].sendall('phase3'.encode('ascii'))
                        phase = 3

        if phase == 3:  # Voting...
            scoreboard = {}
            pm = ''
            for i in range(7):
                if roles[i] != 'ravi' and is_alive[i]:
                    msg = clients[i].recv(1024).decode('ascii')
                    if msg.__contains__('vote'):
                        id_ = int(msg[5:])
                        if names[id_ - 1] in scoreboard:
                            scoreboard[names[id_ - 1]] += 1
                        else:
                            scoreboard[names[id_ - 1]] = 1
                        pm += (names[i] + " voted for " + names[id_ - 1] + '.\n')

            pm += 'Scoreboard:\n'
            for key, value in scoreboard.items():
                pm += str(key) + ' : ' + str(value) + '\n'

            k, v = max(scoreboard.items(), key=lambda k: k[1])
            result = []
            for key in scoreboard:
                if scoreboard[key] == v:
                    result.append(key)
            removing_pms = ['', '', '', '', '', '', '']
            if len(result) == 1:  # remove by voting
                died_ids.append(names.index(result[0]))
                if names.index(result[0]) in shahrvandan_ids:
                    shahrvandan_ids.remove(names.index(result[0]))
                else:
                    mafia_ids.remove(names.index(result[0]))
                for c in clients:
                    if names.index(result[0]) != clients.index(c):
                        if str(roles[names.index(result[0])]).__contains__('mafia'):
                            removing_pms[clients.index(c)] += result[0] + ' is removed. -mafia\n'
                            if len(mafia_ids) == 0:
                                removing_pms[clients.index(c)] += 'The city won.\n'
                                end_game = True
                                break
                        else:
                            removing_pms[clients.index(c)] += result[0] + ' is removed. -shahrvand\n'
                    else:
                        if len(mafia_ids) == 0:
                            removing_pms[clients.index(c)] += 'You were killed.\nThe city won.\n'
                            end_game = True
                            break
                        else:
                            removing_pms[clients.index(c)] += 'You were killed.\n'

            for i in range(7):
                if roles[i] != 'ravi':
                    clients[i].sendall((pm + removing_pms[i]).encode('ascii'))
                else:
                    clients[i].sendall((pm + removing_pms[i] + '|').encode('ascii'))

            msg = clients[ravi_index].recv(1024).decode('ascii')
            if msg == 'next state':
                phase = 1
                for d_id in died_ids:
                    clients[d_id].sendall("Night\n".encode('ascii'))

                for i in range(7):
                    if i in shahrvandan_ids or i in mafia_ids:
                        clients[i].sendall('phase1'.encode('ascii'))


while len(clients) < 7:
    client, address = server.accept()
    print(f"connected with{address}")
    clients.append(client)
    thread = threading.Thread(target=handle, args=(client,))
    thread.start()
