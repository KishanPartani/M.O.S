m = 0
IR = [0 for i in range(4)]
IC = [0 for i in range(2)]
R = [0 for i in range(4)]
C = False
SI = 0

memory = [['\0' for i in range(4)] for j in range(100)]
opfile = open('outputfile.txt', 'w')
input_buffer = []
data_index = 0


def print_memory():
    for i in range(100):
        for j in range(4):
            print(memory[i][j], end=" ", file=opfile)
        print("\n", file=opfile)


def get_data(address):
    global data_index
    i, j = 0, 0
    line = input_buffer[data_index]
    address = (address // 10) * 10
    while (line[i] != '\n'):
        memory[address][j] = line[i]
        i += 1
        j += 1
        if (j == 4):
            j = 0
            address += 1
    data_index += 1


def put_data(address):
    address = (address // 10) * 10
    for i in range(address, address + 10):
        for j in range(4):
            if (memory[i][j] == '\0'):
                break
            print(memory[i][j], end="", file=opfile)
    print('\n', file=opfile)


def terminate():
    print('----------program executed sucessfully----------', file=opfile)
    print("\n", file=opfile)


def load():
    with open("input.txt", "r") as file:
        global input_buffer
        input_buffer = file.readlines()
        counter = -1
        index = 0
        while (index < len(input_buffer)):
            global data_index
            line = input_buffer[index]
            if (line[0].startswith('$')):
                if (line[1:4] == 'AMJ'):  # control card
                    print('Reading Program', file=opfile)
                    global id, time, lines_printed
                    id = line[4:8]
                    time = line[8:12]
                    lines_printed = line[12:16]
                    counter = 0
                elif (line[1:4] == 'DTA'):
                    print('Reading Data\n', file=opfile)
                    counter = 1
                    data_index = index + 1  # index of where data address begins
                    mos_startexecution()
                    index = data_index - 1
                elif (line[1:4] == 'END'):
                    counter = -1
                    global memory, C
                    C = False
                    memory = [['\0' for i in range(4)] for j in range(100)]
                else:
                    print('error in input')
                    exit(-1)

            else:
                if (counter == 0):  # for reading instructions
                    i = 0
                    # print(int(time))
                    for m in range(int(time)):
                        if (line[i] == 'H'):
                            memory[m][0] = line[i]
                            i += 1
                        else:
                            memory[m][0:4] = line[i:i + 4]
                            i += 4
            index += 1


def mos_startexecution():
    IC[0] = 0
    IC[1] = 0
    execute_userprgm()


def master_mode():
    global SI
    if(SI == 1):
        get_data(int(IR[2]) * 10 + int(IR[3]))
    elif(SI == 2):
        put_data(int(IR[2]) * 10 + int(IR[3]))
    elif(SI == 3):
        terminate()


def execute_userprgm():
    for i in range(int(time)):
        global IC, IR, R, C, T, SI
        IR = memory[10 * IC[0] + IC[1]]
        IC[1] += 1  # incrementing IC
        if IC[1] == 10:
            IC[0] += 1
            IC[1] = 0
        inst = "" + IR[0] + IR[1]

        if inst == "LR":
            R = memory[int(IR[2]) * 10 + int(IR[3])]
        elif inst == "SR":
            memory[int(IR[2]) * 10 + int(IR[3])] = R
        elif inst == "CR":
            if (memory[int(IR[2]) * 10 + int(IR[3])] == R):
                C = True
            else:
                C = False
        elif inst == "BT":
            if (C):
                IC[0] = int(IR[2])
                IC[1] = int(IR[3])
        elif inst == "GD":
            SI = 1
            master_mode()
            #get_data(int(IR[2]) * 10 + int(IR[3]))
        elif inst == "PD":
            SI = 2
            master_mode()
            #put_data(int(IR[2]) * 10 + int(IR[3]))
        elif inst == "H\0":
            SI = 3
            master_mode()
            # terminate()
            break


if __name__ == "__main__":
    load()
    opfile.close()
