import random


class PCB:
    def __init__(self, job_id, ttl, tll, ttc, llc, tsc):
        self.job_id = job_id
        self.TTL = ttl   # total time limit
        self.TTC = ttc   # total time counter
        self.TLL = tll   # total line limit
        self.LLC = llc   # line limit counter
        self.TSC = tsc  # time slice counter
        self.curr_IC
        self.PTR
        self.read = False
        self.write = False
        self.program_index = 0
        self.data_index = 0
        self.program_size = 0
        self.data_size = 0
        self.terminate_code = -1

    def incrementLLC(self):
        self.LLC = self.LLC + 1

    def incrementTTC(self):
        self.TTC = self.TTC + 1

    def incrementTSC(self):
        self.TSC = self.TSC + 1


def set_variables():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, CHT_TOT, valid
    m = 0
    valid = False
    IR = [0 for i in range(4)]
    IC = [0 for i in range(2)]
    R = [0 for i in range(4)]
    C = False
    SI = 0
    PI = 0
    TI = 0
    TS = 0
    IOI = 0
    CHT_TOT = [5, 2, 3]
    CH = [False for i in range(3)]  # channel flags
    CHT = [0 for i in range(3)]  # channel timers for all 3 channels
    ebq = []  # empty buffer queue
    ifbq = []  # input buffer full queue
    ofbq = []  # output buffer full queue
    lq = []  # load queue
    rq = []  # ready queue
    ioq = []  # io queue
    tq = []  # terminate queue
    PTR = [0 for i in range(4)]
    used_frames = set()
    supervisory_storage = [
        [['\0' for i in range(4)] for j in range(10)] for k in range(10)]
    memory = [['\0' for i in range(4)] for j in range(300)]
    drum = [['\0' for i in range(4)] for j in range(500)]
    opfile = open('output.txt', 'w')
    input_buffer = []  # size is 40 bytes
    data_index = 0


def start():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH
    set_variables()
    IOI = 1
    start_channel(1)

    while len(rq) > 0 or len(ifbq) > 0 or len(ofbq) > 0:
        execute_usrprgm()
        simulate()
        master_mode()


def master_mode():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH
    pcb = rq[0]
    if (TI == 0 or TI == 1):
        if (SI == 0):
            if (PI == 1):
                # Operation Code Error
                rq[0].terminate_code = 4
                tq.append(rq[0])
                rq.pop()
                memory = [['\0' for i in range(4)] for j in range(300)]
                IR = [0 for i in range(4)]
                IC = [0 for i in range(2)]
                R = [0 for i in range(4)]
                C = False
                return

            elif (PI == 2):
                # Operand Error
                rq[0].terminate_code = 5
                tq.append(rq[0])
                rq.pop()
                memory = [['\0' for i in range(4)] for j in range(300)]
                IR = [0 for i in range(4)]
                IC = [0 for i in range(2)]
                R = [0 for i in range(4)]
                C = False
                return

            elif (PI == 3):  # page fault
                if (valid):  # valid argument passed to master mode function
                    valid_page_fault()
                else:
                    # invalid page fault
                    rq[0].terminate_code = 6
                    tq.append(rq[0])
                    rq.pop()
                    memory = [['\0' for i in range(4)] for j in range(300)]
                    IR = [0 for i in range(4)]
                    IC = [0 for i in range(2)]
                    R = [0 for i in range(4)]
                    C = False
                    return

        else:
            if (SI == 1):  # read function GD
                # move PCB from RQ TO IOQ READ
                rq[0].read = True
                ioq.append(rq[0])
                rq.pop()
                return
            elif (SI == 2):  # write function PD
                # move PCB from RQ TO IOQ WRITE
                rq[0].write = True
                ioq.append(rq[0])
                rq.pop()
                return

            elif (SI == 3):  # terminate successfully
                # MOVE PCB FROM RQ TO TQ
                rq[0].terminat_code = 0
                tq.append(rq[0])
                rq.pop
                memory = [['\0' for i in range(4)] for j in range(300)]
                IR = [0 for i in range(4)]
                IC = [0 for i in range(2)]
                R = [0 for i in range(4)]
                C = False
                return

    elif (TI == 2):
        rq[0].terminate_code = 3
        tq.append(rq[0])
        rq.pop()
        memory = [['\0' for i in range(4)] for j in range(300)]
        IR = [0 for i in range(4)]
        IC = [0 for i in range(2)]
        R = [0 for i in range(4)]
        C = False
        return

    rq.append(rq[0])
    rq.pop()


def start_channel(i):
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH
    if(i == 1):
        IOI -= 1
        CH[0] = True
        CHT[0] = 0
    elif(i == 2):
        IOI -= 2
        CH[1] = True
        CHT[1] = 0

    elif(i == 3):
        IOI -= 4
        CH[2] = True
        CHT[2] = 0


def simulate():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH
    pcb = rq[0]
    pcb.incrementTSC()
    if(pcb.TSC == TS):
        TI = 1

    for i in range(3):
        if(CH[i]):
            CHT[i] += 1
            if(i == 0 and CHT[i] == CHT_TOT[i]):
                IOI += 1
            elif(i == 1 and CHT[i] == CHT_TOT[i]):
                IOI += 2
            elif(i == 2 and CHT[i] == CHT_TOT[i]):
                IOI += 4


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


def execute_usrprgm():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, valid
    if len(rq) == 0:
        return

    time_counter = 0
    pcb = rq[0]    # get pcb of program to be executed

    if (pcb.TTC <= pcb.TTL):   # checking for time limit exceeded error

        global IC, IR, R, C, T, SI, TI, PI, pd_error
        SI = 0
        PI = 0
        TI = 0
        # converting virtual address to real addresss
        inst_count = address_map(10 * IC[0] + IC[1])
        if (inst_count == -1):  # master mode - operand error
            PI = 2
            return
        IR = memory[inst_count]
        print("IR", IR)
        IC[1] += 1  # incrementing IC
        if IC[1] == 10:
            IC[0] += 1
            IC[1] = 0
        inst = "" + IR[0] + IR[1]

        if (inst[0] != "H"):

            if ((IR[2].isnumeric() and IR[3].isnumeric()) == False):  # checking for operand error

                PI = 2
                return
            real_address = address_map(int(IR[2]) * 10 + int(IR[3]))

        if inst == "LR":
            if (real_address == -1):  # invalid page fault
                PI = 3
                valid = False
                return
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
                valid = True
                return
                # pcb.TTC -= 1
            else:
                memory[real_address] = R

        elif inst == "CR":

            if (real_address == -1):  # invalid page fault
                PI = 3
                valid = False
                return

            if (memory[real_address] == R):
                C = True
            else:
                C = False
        elif inst == "BT":
            if (C):
                IC[0] = int(IR[2])
                IC[1] = int(IR[3])

        elif inst == "GD":
            print(inst_count, real_address)
            if (real_address == -1):  # valid page fault
                PI = 3
                SI = 0
                print('valid page fault')
                valid = True
                if IC[1] != 0:
                    IC[1] -= 1
                else:
                    IC[1] = 9
                    IC[0] -= 1
                PI = 0

                return
            SI = 1
            return
            # GD ERROR to be handled in master mode

        elif inst == "PD":
            if (real_address == -1):  # invalid page fault
                PI = 3
                valid = False
                return
            else:
                SI = 2
                return
                # PD ERROR TO BE HANDLED IN MASTER MODE
            #put_data(int(IR[2]) * 10 + int(IR[3]))
        elif inst == "H\0":
            SI = 3
            return

        else:
            PI = 1
            return
        pcb.incrementTTC()

    else:         # time limit exceeded error
        SI = 1
        TI = 2
        return


if __name__ == '__main__':
    start()