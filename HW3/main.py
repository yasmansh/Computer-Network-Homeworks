def is_num(x):
    try:
        int(x)
        return True
    except:
        return False


n = int(input())
distance_vector_tables = []
next_hops = {}
links = {}
data = []
for i in range(n):  # Initialize
    distance_vector_tables.append([])
    data.append([])
    for j in range(n):
        distance_vector_tables[i].append([])
        for k in range(n):
            distance_vector_tables[i][j].append(float('inf'))
    distance_vector_tables[i][i][i] = 0

while True:
    command = input()
    commands = command.split(' ')
    if command.__eq__('end'):
        break
    elif command.__contains__('add_link ') and len(commands) == 4 and is_num(commands[1]) and is_num(commands[2]) and \
            commands[3]:
        node1 = int(commands[1])
        node2 = int(commands[2])
        cost = int(commands[3])
        if node1 >= 0 and node1 < n and node2 >= 0 and node2 < n:
            links[(node1, node2)] = cost
            links[(node2, node1)] = cost
            if cost < distance_vector_tables[node1][node1][node2]:
                distance_vector_tables[node1][node1][node2] = cost
                next_hops[(node1, node2)] = node2
            if cost < distance_vector_tables[node2][node2][node1]:
                distance_vector_tables[node2][node2][node1] = cost
                next_hops[(node2, node1)] = node1
        else:
            print('invalid command')
    elif command.__contains__('send_to_all ') and len(commands) == 2 and is_num(commands[1]) and int(
            commands[1]) >= 0 and int(commands[1]) < n:
        node1 = int(commands[1])
        for i in range(n):
            if (node1, i) in links:
                data[i].append((node1, distance_vector_tables[node1][node1].copy()))
    elif command.__eq__('commit'):
        for i in range(n):
            for j in range(len(data[i])):
                next_hop = data[i][j][0]
                dv = data[i][j][1]
                for k in range(n):  # Update Distance Vectors and Next Hops
                    distance_vector_tables[i][next_hop][k] = dv[k]
                    if i != k and distance_vector_tables[i][i][k] > links[(i, next_hop)] + dv[k]:
                        distance_vector_tables[i][i][k] = links[(i, next_hop)] + dv[k]
                        next_hops[(i, k)] = next_hop

        data.clear()
        for i in range(n):
            data.append([])
    elif command.__contains__('next_hop ') and len(commands) == 3 and is_num(commands[1]) and is_num(commands[2]):
        node1 = int(commands[1])
        node2 = int(commands[2])
        if node1 >= 0 and node1 < n and node2 >= 0 and node2 < n:
            if node1 == node2:
                print('self reference')
            elif distance_vector_tables[node1][node1][node2] == float('inf'):
                print('no path to that node')
            else:
                print(next_hops[(node1, node2)])
        else:
            print('invalid command')
    elif command.__contains__('print') and len(commands) == 2 and is_num(commands[1]) and int(
            commands[1]) >= 0 and int(commands[1]) < n:
        node1 = int(commands[1])
        for i in range(n):
            s = ''
            for j in range(n):
                s += str(distance_vector_tables[node1][i][j]) + '    '
            print(s)
        print()
    else:
        print('invalid command')
