import random


class PCB:
    def __init__(self, job_id, ttl, tll, ttc, llc, tsc):
        self.job_id = job_id
        self.TTL = ttl   # total time limit
        self.TTC = ttc   # total time counter
        self.TLL = tll   # total line limit
        self.LLC = llc   # line limit counter
        self.TSC = tsc  # time slice counter
        self.curr_IC = [0 for i in range(2)]
        self.PTR = 0
        self.read = False
        self.write = False
        self.program_index = 0
        self.data_index = 0
        self.program_frames = 0
        self.data_frames = 0
        self.terminate_code = -1
        self.supervisory_indices = []

    def incrementLLC(self):
        self.LLC = self.LLC + 1

    def incrementTTC(self):
        self.TTC = self.TTC + 1

    def incrementTSC(self):
        self.TSC = self.TSC + 1


def print_drum(max_index=500):
    global drum
    print("Drum")
    for i in range(max_index):
        print(drum[i])


def set_variables():
    global m, drum_index, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, CHT_TOT, valid, buffer_status, counter_for_job, line_index, buffer_index, task
    m = 0
    line_index = 0
    counter_for_job = -1
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
    data_index = 0
    buffer_status = [0 for i in range(10)]
    buffer_index = 0
    task = ''
    drum_index = 0


def start():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, buffer_status
    set_variables()
    IOI = 0
    start_channel(1)
    print("IOI in start", IOI)
    simulate()
    master_mode()
    print(len(rq))
    time = 0
    # while ((len(rq) > 0 or len(ifbq) > 0 or len(ofbq) > 0) or time < 5):
    for i in range(0, 14):
        global CHT
        execute_usrprgm()
        simulate()
        master_mode()
        print('hi')
        print(CHT)
        time += 1
    print_drum()


def free_drum_track(start=0):
    global drum
    for i in range(start, 500):
        if(drum[i][0] == '\0'):
            return i
    for i in range(0, start):
        if(drum[i][0] == '\0'):
            return
    return -1


def interrupt_routine(rnum):
    print("interrrupt routine", rnum)
    global buffer_index, input_buffer, counter_for_job, line_index, eb, IOI, task, lq, drum_index
    if(rnum == 1):
        #print("supervisory storage",supervisory_storage)
        global buffer_index
        pcb = PCB(0, 0, 0, 0, 0, 0)
        index = 0
        eb = [['\0' for i in range(4)] for i in range(10)]
        for i in range(len(buffer_status)):
            if(buffer_status[i] == 0):
                print("i of supervisory", i)
                # eb=supervisory_storage[i]
                buffer_status[i] = 1
                break
        # code for interrupt routine 1
        pcb.supervisory_indices.append(i)
        print("input buffer", input_buffer)
        if(buffer_index == len(input_buffer)):
            return
        line = input_buffer[buffer_index]
        while(True):
            print("PCB Contents", pcb.data_frames, " ", pcb.program_frames)
            if(index == 10):
                # print(eb)
                supervisory_storage[i] = eb
                ifbq.append(eb)
                index = 0
                if(counter_for_job == 0):
                    pcb.program_frames += 1
                elif(counter_for_job == 1):
                    pcb.data_frames += 1

                for i in range(len(buffer_status)):
                    if(buffer_status[i] == 0):
                        # eb=supervisory_storage[i]
                        print("i of supervisory this", i)
                        buffer_status[i] = 1
                        eb = [['\0' for i in range(4)] for i in range(10)]
                        break
                pcb.supervisory_indices.append(i)

            if(line_index >= len(line)):
                if(line[0] != '$'):
                    # print(eb)
                    supervisory_storage[i] = eb
                    ifbq.append(eb)
                    if(counter_for_job == 0):
                        pcb.program_frames += 1
                    elif(counter_for_job == 1):
                        pcb.data_frames += 1
                    for i in range(len(buffer_status)):
                        if(buffer_status[i] == 0):
                            print("i of supervisory", i)
                            # eb=supervisory_storage[i]
                            eb = [['\0' for i in range(4)] for i in range(10)]
                            buffer_status[i] = 1
                            break
                    pcb.supervisory_indices.append(i)

                line_index = 0
                buffer_index += 1
                index = 0
                if(buffer_index == len(input_buffer)):
                    IOI = -1
                    break
                line = input_buffer[buffer_index]

            if (line[0].startswith('$')):
                if (line[1:4] == 'AMJ'):
                    id = line[4:8]
                    time = line[8:12]
                    lines_printed = line[12:16]
                    pcb.job_id = id  # initialize PCB    ##needs to be changed
                    pcb.TTL = int(time)
                    pcb.TLL = int(lines_printed)
                    frame_num = (random.randint(0, 29))
                    used_frames.add(frame_num)
                    counter_for_job = 0
                    line_index += 12

                elif(line[1:4] == 'DTA'):
                    counter_for_job = 1
                    line_index += 4
                    pcb.data_index = pcb.program_index+pcb.program_frames+1
                elif(line[1:4] == 'END'):
                    supervisory_storage[i] = eb
                    print("END CARD")
                    lq.append(pcb)
                    print("JOB ID : ", pcb.job_id)
                    line_index += 4
                    buffer_index += 1
                    start_channel(3)  # start input spooling
                    task = 'IS'
                    print("\n\nProgram done \n\n")
                    return
                index -= 1
            else:
                if(counter_for_job == 0):  # for program card
                    if(line[line_index] == 'H'):
                        eb[index][0] = line[line_index]
                        line_index += 1
                    elif(line[line_index] == '\n'):
                        line_index += 1
                    else:
                        eb[index][0:4] = line[line_index:line_index+4]
                        line_index += 4

                elif(counter_for_job == 1):  # for data card
                    eb[index][0:4] = line[line_index:line_index+4]
                    line_index += 4
            index = index+1

    elif(rnum == 2):
        # code for interrupt routine 2
        pass
    elif(rnum == 3):
        print("IR CALLED")

        # code for interrupt routine 3
        if task == 'IS':
            if(free_drum_track() == -1):
                print('NO SPACE IN DRUM')
                return
            if(len(ifbq) == 0):
                return
            if(len(lq) != 0):
                cur_pcb = lq.pop(0)
                cur_pcb.P = []
                cur_pcb.D = []
                cur_pcb.O = []
                print(len(ifbq))
                for i in range(cur_pcb.program_frames):
                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ifbq.pop(0)
                    cur_pcb.P.append(drum_index)
                    drum_index += 10

                for i in range(cur_pcb.data_frames):
                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ifbq.pop(0)
                    cur_pcb.D.append(drum_index)
                    drum_index += 10

                for index in cur_pcb.supervisory_indices:
                    supervisory_storage[index] = [
                        ["\0" for i in range(4)] for j in range(10)]
                    buffer_status[index] = 0

                for i in range(cur_pcb.TLL):
                    # check this if print malfunctions
                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ['' for i in range(10)]
                    cur_pcb.O.append(drum_index)
                    drum_index += 10
                lq.append(cur_pcb)
            # pcb=lq[0]
            #print("checking data index",pcb.supervisory_indices)

        elif task == 'OS':
            pass
        elif task == 'LD':
            cur_pcb = lq.pop(0)
            # initialise page table for the process
            frame_num = (random.randint(0, 29))
            used_frames.add(frame_num)   # add frame to used frames set
            frame_num *= 10
            # initialise page table register
            PTR[1] = frame_num // 100
            frame_num = frame_num % 100
            PTR[2] = frame_num // 10
            PTR[3] = frame_num % 10
            cur_pcb.PTR = PTR   # Save PTR into PCB

            # initialising memory frame and adding it to Page Table
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

            frame_num_p = frame_num_prog * 10  # address where program is stored

            for index in cur_pcb.P:
                memory[frame_num_p:frame_num_p+10] = drum[index:index+10]
                frame_num_p += 10

            rq.append(cur_pcb)
            pass
        elif task == 'RD':
            pass
        elif task == 'WT':
            pass
        pass


def master_mode():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, buffer_status
    if(len(rq) != 0):
        pcb = rq[0]
        print("master mode")
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

                elif (PI == 3):  # page fault
                    if (valid):  # valid argument passed to master mode function
                        valid_page_fault()
                        rq.append(rq[0])
                        rq.pop()

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

            else:
                if (SI == 1):  # read function GD
                    # move PCB from RQ TO IOQ READ
                    rq[0].read = True
                    ioq.append(rq[0])
                    rq.pop()

                elif (SI == 2):  # write function PD
                    # move PCB from RQ TO IOQ WRITE
                    rq[0].write = True
                    ioq.append(rq[0])
                    rq.pop()

                elif (SI == 3):  # terminate successfully
                    # MOVE PCB FROM RQ TO TQ
                    rq[0].terminate_code = 0
                    tq.append(rq[0])
                    rq.pop
                    memory = [['\0' for i in range(4)] for j in range(300)]
                    IR = [0 for i in range(4)]
                    IC = [0 for i in range(2)]
                    R = [0 for i in range(4)]
                    C = False

        elif (TI == 2):
            rq[0].terminate_code = 3
            tq.append(rq[0])
            rq.pop()
            memory = [['\0' for i in range(4)] for j in range(300)]
            IR = [0 for i in range(4)]
            IC = [0 for i in range(2)]
            R = [0 for i in range(4)]
            C = False

    print("IOI in master mode", IOI)
    if IOI == 1:
        print("interrupt routine 1")
        interrupt_routine(1)
    elif IOI == 2:
        interrupt_routine(2)
    elif IOI == 3:
        interrupt_routine(2)
        interrupt_routine(1)
    elif IOI == 4:
        interrupt_routine(3)
    elif IOI == 5:
        interrupt_routine(1)
        interrupt_routine(3)
    elif IOI == 6:
        interrupt_routine(3)
        interrupt_routine(2)
    elif IOI == 7:
        interrupt_routine(2)
        interrupt_routine(1)
        interrupt_routine(3)


def start_channel(i):
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, buffer_status
    if(i == 1):
        #IOI -= 1
        CH[0] = True
        CHT[0] = 0  # Channel Timer
    elif(i == 2):
        #IOI -= 2
        CH[1] = True
        CHT[1] = 0

    elif(i == 3):
        #IOI -= 4
        CH[2] = True
        CHT[2] = 0


def simulate():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, buffer_status
    if(len(rq) != 0):
        pcb = rq[0]
        pcb.incrementTSC()
        if(pcb.TSC == TS):
            TI = 1
    # NEEDS TO BE REMOVED
    print(CH)
    print(CHT)
    print(CHT_TOT)
    for i in range(3):
        if(CH[i]):
            CHT[i] += 1
            print("CHANNEL ", i, CHT[i])
            if(i == 0 and CHT[i] == CHT_TOT[i]):
                IOI += 1
                CH[i] = False
                CHT[i] = 0
            elif(i == 1 and CHT[i] == CHT_TOT[i]):
                IOI += 2
                CH[i] = False
                CHT[i] = 0
            elif(i == 2 and CHT[i] == CHT_TOT[i]):
                IOI += 4
                CH[i] = False
                CHT[i] = 0


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
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, valid, buffer_status
    if len(rq) == 0:
        return
    print("execute user program")
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
    global input_buffer
    with open("input.txt", "r") as file:
        input_buffer = file.readlines()
    print("main started")
    print(input_buffer)
    start()
