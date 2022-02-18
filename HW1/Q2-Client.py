import socket, threading

host = '127.0.0.1'
port = 8072

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def handle():
    id = -1
    role = ''
    is_alive = True
    save_yourself = False
    alive_players_id = []
    godfather_is_alive = True
    mafia_sade_is_alive = True

    try:
        msg = input("Your name:\n")
        client.sendall(msg.encode('ascii'))
        msg = client.recv(1024).decode('ascii')
        print(msg)
        if msg == 'Your role: ravi':
            role = 'ravi'
            msg = input("Define roles with -set roles :\n")
            client.sendall(msg.encode('ascii'))
            msg = client.recv(1024).decode('ascii')
            print(msg)  # roles
            msg = input("Go to the next game mode with -next state :\n")
            client.sendall(msg.encode('ascii'))
            phase = 1
        elif msg.__contains__("Your role:"):
            index = msg.rindex('-')
            role = msg[11:index]
            id = int(msg[index + 10:])
            if role == 'mafia-pedar khaande':
                msg = client.recv(1024).decode('ascii')
                alives = msg.split(' ')
                for i in range(len(alives) - 1):
                    alive_players_id.append(int(alives[i]))
                print("shahrvandan :" + str(alive_players_id))
            elif role == 'mafia-sade':
                msg = client.recv(1024).decode('ascii')
                index = msg.index('gadfather:')
                alives = msg[:index - 1].split(' ')
                for i in range(len(alives)):
                    alive_players_id.append(int(alives[i]))
                godfather_id = int(msg[index + 10:index + 11])
                print("shahrvandan :" + str(alive_players_id) + "\nGodfather ID:" + str(godfather_id))

        #####################
        phase = 1
        end_game = False
        while not end_game and is_alive:

            msg = client.recv(1024).decode('ascii')
            if msg.__contains__('won'):
                print(msg)
                end_game = True
                break

            if msg.__contains__('phase'):
                phase = int(msg[msg.index('phase') + 5])

                if phase == 1:
                    print('Night')

                    if role == 'mafia-sade' and is_alive:
                        if godfather_is_alive:
                            msg = input("Suggest your target to the godfather with -offer <player_id>\n")
                            client.sendall((msg + '\t\t\t').encode('ascii'))
                        else:  # as godfather
                            msg = input("Select the player ID with -select <player_id>:\n")
                            client.sendall(msg.encode('ascii'))

                    if role == 'mafia-pedar khaande' and is_alive:
                        if mafia_sade_is_alive:
                            msg = client.recv(1024).decode('ascii')  # offer
                            print(msg)

                        msg = input("Select the player ID with -select <player_id>:\n")
                        client.sendall((msg + '\t\t\t').encode('ascii'))

                    if role == 'pezeshk' and is_alive:
                        msg = input("Select the player ID with -select <player_id>:\n")
                        client.sendall((msg + '\t\t\t').encode('ascii'))
                        if (int(msg[6:]) - 1) == id and not save_yourself:
                            save_yourself = True
                        elif (int(msg[6:]) - 1) == id:
                            msg = client.recv(1024).decode('ascii')
                            print(msg)
                            msg = input()
                            client.sendall((msg + '\t\t\t').encode('ascii'))

                    if role == 'karagah' and is_alive:
                        msg = input("Select the player ID with -select <player_id>:\n")
                        client.sendall((msg + '\t\t\t\t\t').encode('ascii'))
                        msg = client.recv(1024).decode('ascii')  # Natije ye estelam
                        print(msg)

                    if role.__contains__('shahrvand'):
                        print('Please be quiet.')

                    if role == 'ravi':
                        msg = client.recv(1024).decode('ascii')
                        while not msg.__contains__('|'):
                            print(msg)
                            msg = client.recv(1024).decode('ascii')

                        msg = input("Go to the next game mode with -next state :\n")
                        client.sendall(msg.encode('ascii'))
                        phase = 2

                elif phase == 2 and is_alive:
                    print("Day")
                    if not msg == 'phase2':
                        print(msg.replace('phase2', ''))

                    if msg.__contains__('You were killed.'):
                        is_alive = False
                        print('YOU ARE A VIEWER.')

                    if role != 'ravi' and is_alive:
                        msg = input("Say your comment with -say <message>\n")
                        client.sendall((msg + '\t\t\t').encode('ascii'))
                        print('-->' + msg[3:])

                        msg = client.recv(1024).decode('ascii')
                        print(msg)  # chat
                        msg = client.recv(1024).decode('ascii')
                        if msg.__contains__('phase3'):
                            phase = 3

                        if phase == 3 and is_alive:
                            print("Voting...")
                            msg = input("Vote for your target with -vote <player_id>\n")
                            client.sendall(msg.encode('ascii'))

                            msg = client.recv(1024).decode('ascii')
                            print(msg)

                            if msg.__contains__(' is removed. -mafia') and role == 'mafia-sade':
                                godfather_is_alive = False

                            elif msg.__contains__(' is removed. -mafia') and role == 'mafia-pedar khaande':
                                mafia_sade_is_alive = False

                            if msg.__contains__('won'):
                                end_game = True
                                break

                            if msg.__contains__('You were killed.'):
                                is_alive = False
                                print('You are a viewer.')
                                break

                            if not end_game and is_alive:
                                msg = client.recv(1024).decode('ascii')
                                if msg == 'phase1':
                                    phase = 1

                    elif role == 'ravi':
                        msg = client.recv(1024).decode('ascii')
                        msg.replace('|', '')
                        print(msg)  # chat

                        if msg.__contains__('won'):
                            end_game = True
                            break
                        else:
                            msg = input("Go to the next game mode with -next state :\n")
                            client.sendall(msg.encode('ascii'))

                            phase = 3
                            msg = client.recv(1024).decode('ascii')
                            print(msg) #voting msg

                            msg = input("Go to the next game mode with -next state :\n")
                            client.sendall(msg.encode('ascii'))
                            phase = 1
                            msg = 'phase1'


        while not end_game:  # Viewer
            msg = client.recv(1024).decode('ascii')
            print(msg)
            if msg.__contains__("won"):
                end_game = True
    except:
        pass


# except:
#     client.close()


handle_thread = threading.Thread(target=handle)
handle_thread.start()
