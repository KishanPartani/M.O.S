import random

m = 0
IR = [0 for i in range(4)]
IC = [0 for i in range(2)]
R = [0 for i in range(4)]
C = False
SI = 0
PI = 0
TI = 0
PTR = [0 for i in range(4)]

used_frames = set()

memory = [['\0' for i in range(4)] for j in range(300)]
opfile = open('output.txt', 'w')
input_buffer = []  # size is 40 bytes
data_index = 0

pd_error = 0   # for line limit exceeded
gd_error = 0   # for out of data


class PCB:
    def __init__(self, job_id, ttl, tll, ttc, llc):
        self.job_id = job_id
        self.TTL = ttl   # total time limit
        self.TTC = ttc   # total time counter
        self.TLL = tll   # total line limit
        self.LLC = llc   # line limit counter

    def incrementLLC(self):
        self.LLC = self.LLC + 1

    def incrementTTC(self):
        self.TTC = self.TTC + 1


def print_memory():
    for i in range(300):
        for j in range(4):
            print(memory[i][j], end=" ", file=opfile)
        print("\n", file=opfile)


def get_data(address):
    global data_index, gd_error
    i, j = 0, 0
    line = input_buffer[data_index]
    if (line[0] == "$"):  # checking for out of data error
        gd_error = -1
        return
    address = (address // 10) * 10
    while (line[i] != '\n'):          # adding data to the memory at received address
        memory[address][j] = line[i]
        i += 1
        j += 1
        if (j == 4):
            j = 0
            address += 1
    data_index += 1


def put_data(address):
    global pd_error
    if (pcb.LLC >= pcb.TLL):  # checking for line limit exceeded
        pd_error = -1
        return
    address = (address // 10) * 10

    for i in range(address, address + 10):   # printing entire block to file
        for j in range(4):
            if (memory[i][j] == '\0'):
                break
            print(memory[i][j], end="", file=opfile)
    print('\n', file=opfile)
    pcb.incrementLLC()


def terminate(em):
    if (em == 0):
        print("Program Executed Sucessfully\n", file=opfile)
    elif (em == 1):
        print("Out of Data Error\n", file=opfile)
    elif (em == 2):
        print("Line Limit Exceeded \n ", file=opfile)
    elif (em == 3):
        print("Time Limit Exceeded\n", file=opfile)
    elif (em == 4):
        print("Operation Code Error\n", file=opfile)
    elif (em == 5):
        print("Operand Error\n", file=opfile)
    elif (em == 6):
        print("Invalid Page Fault\n", file=opfile)

    print("---Interrupt Status---", file=opfile)
    print("SI", SI, file=opfile)
    print("PI", PI, file=opfile)
    print("TI", TI, file=opfile)
    print("---Register Status---", file=opfile)
    print("R", R, file=opfile)
    print("IC", IC, file=opfile)
    print("IR", IR, file=opfile)
    print("C", C, file=opfile)
    print("PTR", PTR, file=opfile)
    print(
        "----------------------------------------------------------------------------",
        file=opfile)
    print("\n", file=opfile)


def load():
    with open("input.txt", "r") as file:
        global input_buffer, memory

        input_buffer = file.readlines()
        counter = -1
        index = 0
        while (index < len(input_buffer)):
            global data_index, pcb, id, time, lines_printed, PTR, used_frames, memory, C, IR, IC, R, SI, PI, TI, pd_error, gd_error
            line = input_buffer[index]
            if (line[0].startswith('$')):
                if (line[1:4] == 'AMJ'):  # control card

                    print('Reading Program', file=opfile)

                    id = line[4:8]
                    time = line[8:12]
                    lines_printed = line[12:16]
                    counter = 0
                    pcb = PCB(id, int(time), int(lines_printed), 0,
                              0)  # initialize PCB
                    # initialise frame for page table
                    frame_num = (random.randint(0, 29))
                    used_frames.add(frame_num)   # add frame to used frames set
                    frame_num *= 10
                    # initialise page table register
                    PTR[1] = frame_num // 100
                    frame_num = frame_num % 100
                    PTR[2] = frame_num // 10
                    PTR[3] = frame_num % 10

                elif (line[1:4] == 'DTA'):
                    print('Reading Data\n', file=opfile)
                    counter = 1
                    data_index = index + 1  # index of where data address begins
                    mos_startexecution()
                    index = data_index - 1

                elif (line[1:4] == 'END'):
                    counter = -1
                    print("new prog")
                    # resetting all globals
                    C = False
                    memory = [['\0' for i in range(4)] for j in range(300)]

                    IR = [0 for i in range(4)]
                    IC = [0 for i in range(2)]
                    R = [0 for i in range(4)]
                    C = False
                    SI = 0  # need to be looked
                    PI = 0
                    TI = 0
                    PTR = [0 for i in range(4)]
                    used_frames.clear()
                    counter = -1
                    pd_error = 0
                    gd_error = 0
                else:
                    print('error in input')
                    exit(-1)

            else:
                if (counter == 0):  # for reading instructions
                    # initialising frame for program
                    frame_num_prog = random.randint(0, 29)
                    while frame_num_prog in used_frames:  # finding unique frame
                        frame_num_prog = random.randint(0, 29)
                    used_frames.add(frame_num_prog)

                    pt_num = int(PTR[1]) * 100 + int(PTR[2]) * 10 + int(
                        PTR[3])  # updating page table entry

                    memory[pt_num][2] = frame_num_prog // 10
                    memory[pt_num][3] = frame_num_prog % 10
                    memory[pt_num][0] = 0
                    memory[pt_num][1] = 0

                    i = 0
                    # print(int(time))

                    frame_num_p = frame_num_prog * 10  # address where program is stored

                    while (i < len(line)):

                        if (line[i] == 'H'):

                            memory[frame_num_p][0] = line[i]
                            i += 1  # since H has no operands associated with it
                            frame_num_p += 1
                        else:
                            memory[frame_num_p][0:4] = line[i:i + 4]

                            i += 4
                            frame_num_p += 1
                        if (frame_num_p % 10 == 0):  # if frame size exceeded- assign new frame
                            frame_num_prog = random.randint(0, 29)
                            while frame_num_prog in used_frames:
                                frame_num_prog = random.randint(0, 29)
                            used_frames.add(frame_num_prog)
                            frame_num_p = frame_num_prog * 10
                            pt_num += 1  # increment page table index
                            # update page table entry
                            memory[pt_num][2] = frame_num_prog // 10
                            memory[pt_num][3] = frame_num_prog % 10
                            memory[pt_num][0] = 0
                            memory[pt_num][1] = 0
            index += 1


def mos_startexecution():
    IC[0] = 0
    IC[1] = 0
    # print(PTR)
    execute_userprgm()


def master_mode(valid=False):
    global SI, TI, PI
    if (TI == 0):
        if (SI == 0):
            if (PI == 1):
                terminate(4)  # Operation Code Error
            elif (PI == 2):
                terminate(5)  # Operand Error
            elif (PI == 3):  # page fault
                if (valid):  # valid argument passed to master mode function
                    valid_page_fault()
                else:
                    terminate(6)  # invalid page fault
        else:
            if (SI == 1):  # read function GD
                get_data(address_map(int(IR[2]) * 10 + int(IR[3])))
            elif (SI == 2):  # write function PD
                put_data(address_map(int(IR[2]) * 10 + int(IR[3])))
            elif (SI == 3):  # terminate successfully
                terminate(0)

    elif (TI == 2):

        if (SI == 0):
            if (PI == 1):
                terminate(3)  # Time Limit Exceeded
                terminate(4)
            elif (PI == 2):
                terminate(3)  # Time Limit Exceeded
                # terminate(5)
            elif (PI == 3):
                terminate(3)  # Time Limit Exceeded

        else:
            if (SI == 1):
                terminate(3)
            elif (SI == 2):
                put_data(address_map(int(IR[2]) * 10 + int(IR[3])))
                terminate(3)
            elif (SI == 3):
                terminate(0)


def address_map(VA):

    global PTR, memory
    # first we get page table entry
    pte = (int(PTR[1]) * 100 + int(PTR[2]) * 10 + int(PTR[3])) + VA // 10

    if memory[pte][0] == '\0':  # checking if anything is present in page table entry
        return -1  # if not invoke page fault

    # calculate memory frame entry from pte
    addr = int(memory[pte][2]) * 10 + int(memory[pte][3])
    RA = addr * 10 + VA % 10  # calculate real address
    return RA


def valid_page_fault():
    global used_frames, memory, PTR
    frame_num_data = random.randint(0, 29)  # initialise a new frame for data
    while frame_num_data in used_frames:
        frame_num_data = random.randint(0, 29)
    used_frames.add(frame_num_data)
    # find page table index which is empty
    c_ptr = (int(PTR[1]) * 100 + int(PTR[2]) * 10 + int(PTR[3]))
    while (memory[c_ptr][0] != '\0'):
        c_ptr += 1
    # add page table entry
    memory[c_ptr][2] = frame_num_data // 10
    memory[c_ptr][3] = frame_num_data % 10
    memory[c_ptr][0] = 0
    memory[c_ptr][1] = 0

    print(memory[c_ptr])


def execute_userprgm():
    time_counter = 0
    while (1):

        if (pcb.TTC <= pcb.TTL):   # checking for time limit exceeded error

            global IC, IR, R, C, T, SI, TI, PI, pd_error
            SI = 0
            PI = 0
            TI = 0
            # converting virtual address to real addresss
            inst_count = address_map(10 * IC[0] + IC[1])
            print("IR", IR)
            if (inst_count == -1):  # master mode - operand error
                PI = 2
                master_mode()
                break
            IR = memory[inst_count]
            IC[1] += 1  # incrementing IC
            if IC[1] == 10:
                IC[0] += 1
                IC[1] = 0
            inst = "" + IR[0] + IR[1]

            if (inst[0] != "H"):

                if ((IR[2].isnumeric() and IR[3].isnumeric()) == False):  # checking for operand error

                    PI = 2
                    master_mode()

                    break
                real_address = address_map(int(IR[2]) * 10 + int(IR[3]))

            if inst == "LR":
                if (real_address == -1):  # invalid page fault
                    PI = 3
                    master_mode()
                    break
                R = memory[real_address]

            elif inst == "SR":
                if (real_address == -1):  # valid page fault
                    PI = 3
                    # decrementing IC
                    if IC[1] != 0:
                        IC[1] -= 1
                    else:
                        IC[1] = 9
                        IC[0] -= 1
                    master_mode(valid=True)
                    time_counter -= 1
                    # pcb.TTC -= 1
                    continue
                else:
                    memory[real_address] = R

            elif inst == "CR":

                if (real_address == -1):  # invalid page fault
                    PI = 3
                    master_mode()
                    break
                if (memory[real_address] == R):
                    C = True
                else:
                    C = False
            elif inst == "BT":
                if (C):
                    IC[0] = int(IR[2])
                    IC[1] = int(IR[3])

            elif inst == "GD":

                if (real_address == -1):  # valid page fault
                    PI = 3
                    SI = 0
                    master_mode(valid=True)
                    if IC[1] != 0:
                        IC[1] -= 1
                    else:
                        IC[1] = 9
                        IC[0] -= 1
                    PI = 0
                    time_counter -= 1
                    # pcb.TTC -= 1
                    continue
                SI = 1

                master_mode()
                if (gd_error == -1):  # out of data
                    terminate(1)
                    break
                #get_data(int(IR[2]) * 10 + int(IR[3]))
            elif inst == "PD":
                if (real_address == -1):  # invalid page fault
                    PI = 3
                    master_mode()
                    break
                else:
                    SI = 2
                    master_mode()
                    if (pd_error == -1):  # if line limit exceeds
                        terminate(2)
                        break

                #put_data(int(IR[2]) * 10 + int(IR[3]))
            elif inst == "H\0":
                SI = 3
                master_mode()
                # terminate()
                break

            else:
                PI = 1
                master_mode()
                break
            pcb.incrementTTC()

        else:         # time limit exceeded error
            SI = 1
            TI = 2
            master_mode()
            break
        time_counter += 1


if __name__ == "__main__":
    load()
    opfile.close()
