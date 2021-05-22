from ast import Pass
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
        self.PTR = [0 for i in range(4)]
        self.read = False
        self.write = False
        self.program_index = 0
        self.data_index = 0
        self.program_frames = 0
        self.data_frames = 0
        self.terminate_code = -1
        self.supervisory_indices = []
        self.data_index_check = 0
        self.program_index_check = 0
        self.op_index_check = 0
        self.P = []
        self.D = []
        self.O = []
        self.real_address = 0
        self.error=0

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
    global m, drum_index,mem_flag, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CHT_TOT, valid, buffer_status, counter_for_job, line_index, buffer_index, task, lq_am
    m = 0
    mem_flag=False
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
    lq_am = [] # load queue for Auxiliary Memory
    rq = []  # ready queue
    ioq = []  # io queue
    tq = []  # terminate queue
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
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, buffer_status
    set_variables()
    IOI = 1
    start_channel(1)
    print("IOI in start", IOI)
    simulate()
    master_mode()
    time = 0
    while ((len(rq) > 0 or len(ifbq) > 0 or len(ofbq) > 0 or len(ioq)>0 or len(lq)>0 or time<10) and (time<=25)):
        print("Length of rq",len(rq))
        print("Length of ifbq",len(ifbq))
        print("Length of ofbq",len(ofbq))
        print("Length of ioq",len(ioq))
        print("Length of lq",len(lq))

        global CHT
        execute_usrprgm()
        simulate()
        master_mode()
        time+=1
    print("Length of rq",len(rq))
    print("Length of ifbq",len(ifbq))
    print("Length of ofbq",len(ofbq))
    print("Length of ioq",len(ioq))
    print("Length of lq",len(lq))
    #print_drum()
    #display(memory,300)
    #display(drum,500)

def free_drum_track(start=0):
    global drum
    for i in range(start, 500):
        if(drum[i][0] == '\0'):
            return i
    for i in range(0, start):
        if(drum[i][0] == '\0'):
            return
    return -1

def display(x,y):
    for i in range(y):
        print(i, x[i])

def interrupt_routine(rnum):
    print("interrrupt routine", rnum)
    global buffer_index, input_buffer, counter_for_job, line_index, eb, IOI, task, lq, drum_index, lq_am,mem_flag, memory,drum
    if(rnum == 1):
        #print("supervisory storage",supervisory_storage)
        global buffer_index
        pcb = PCB(0, 0, 0, 0, 0, 0)
        index = 0
        eb = [['\0' for i in range(4)] for i in range(10)]
        for i in range(len(buffer_status)):
            if(buffer_status[i] == 0):
                #print("i of supervisory", i)
                # eb=supervisory_storage[i]
                buffer_status[i] = 1
                break
        # code for interrupt routine 1
        pcb.supervisory_indices.append(i)
        # print("input buffer", input_buffer)
        if(buffer_index == len(input_buffer)):
            return
        line = input_buffer[buffer_index]
        while(True):
            # print("PCB Contents", pcb.data_frames, " ", pcb.program_frames)
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
                        #print("i of supervisory this", i)
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
                            #print("i of supervisory", i)
                            # eb=supervisory_storage[i]
                            eb = [['\0' for i in range(4)] for i in range(10)]
                            buffer_status[i] = 1
                            break
                    pcb.supervisory_indices.append(i)

                line_index = 0
                buffer_index += 1
                index = 0
                if(buffer_index == len(input_buffer)):
                    #IOI = -1           ##needs to be checked
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
                    #print("JOB ID : ", pcb.job_id)
                    line_index += 4
                    buffer_index += 1
                    task = 'IS'
                    IOI+=4
                    start_channel(3)  # start input spooling
                    
                    start_channel(1)
                    print("CH after ch3 in end",CH)
                    # print("\n\nProgram done \n\n")
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
        # if(CH[0]==False):
        #     IOI+=1
        start_channel(1)
        print("CH after ch3 in end",CH)
    elif(rnum == 2):
        # code for interrupt routine 2
        # if(CH[1]==False):
        #     IOI+=2
        start_channel(2)
        print("CH after ch3 in end",CH)
    elif(rnum == 3):
        print("Started channel 3, task=",task)
        if task == 'IS':
            if(free_drum_track() == -1):
                print('NO SPACE IN DRUM')
                return
            if(len(lq) != 0):
                cur_pcb = lq.pop(0)
                if(len(ifbq) == 0 and cur_pcb.op_index_check == cur_pcb.TLL ):
                    return

                print("lq in is",len(lq))
                if(cur_pcb.program_index_check < cur_pcb.program_frames):
                    #for i in range(cur_pcb.program_frames):

                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ifbq.pop(0)
                    cur_pcb.P.append(drum_index)
                    print("NEW NEW ",cur_pcb.P)
                    print("PCB id",cur_pcb.job_id)
                    drum_index += 10
                    cur_pcb.program_index_check += 1
                    lq.insert(0, cur_pcb)
                    print("lq prog",cur_pcb.program_index_check," ", cur_pcb.program_frames)
                    return

                if((cur_pcb.program_index_check == cur_pcb.program_frames) and (cur_pcb.data_index_check < cur_pcb.data_frames)):
                    #for i in range(cur_pcb.data_frames):
                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ifbq.pop(0)
                    cur_pcb.D.append(drum_index)
                    drum_index += 10
                    cur_pcb.data_index_check += 1
                    print("lq data",cur_pcb.data_index_check," ", cur_pcb.data_frames)
                    print("lq op",cur_pcb.op_index_check, " ", cur_pcb.TLL)
                    lq.insert(0, cur_pcb)
                    return

                else:
                    #for i in range(cur_pcb.TLL):
                        # check this if print malfunctions
                    print("shify op frames")
                    drum_index = free_drum_track(drum_index)
                    if(drum_index == -1):
                        print('NO SPACE IN DRUM')
                        return
                    drum[drum_index:drum_index+10] = ['' for i in range(10)]
                    cur_pcb.O.append(drum_index)
                    drum_index += 10
                    cur_pcb.op_index_check += 1
                    lq.insert(0, cur_pcb)
                    print("lq check in if",cur_pcb.op_index_check," ", cur_pcb.TLL)

                if(cur_pcb.op_index_check == cur_pcb.TLL):
                    print("after lq check")
                    for index in cur_pcb.supervisory_indices:
                        supervisory_storage[index] = [
                            ["\0" for i in range(4)] for j in range(10)]
                        buffer_status[index] = 0
                    #lq.append(cur_pcb)
                    task = 'LD'
                    print("hello buns")
                    lq.pop(0)
                    lq_am.append(cur_pcb)
                    print("New current pcb",cur_pcb.P)
                    print("lqam",lq_am)
            # pcb=lq[0]
            #print("checking data index",pcb.supervisory_indices)

        elif task == 'OS':
            pass
        elif task == 'LD':
            
            if(len(lq_am) != 0 and mem_flag==False):
                print("\n\nIn Load...\n\n")
                mem_flag==True
                cur_pcb = lq_am.pop(0)
                # print("Element from lq_am",cur_pcb)
                # initialise page table for the process
                frame_num = (random.randint(0, 29))
                used_frames.add(frame_num)   # add frame to used frames set
                frame_num *= 10
                # initialise page table register
                PTR=[0 for i in range(4)]
                PTR[0] = 0
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
                print("\n\nPTR\n\n",PTR)
                pt_num = int(PTR[1]) * 100 + int(PTR[2]) * 10 + int(
                    PTR[3])  # updating page table entry
                
                # print("\n\npt_num ",pt_num," \n\n")
                memory[pt_num][2] = frame_num_prog // 10
                memory[pt_num][3] = frame_num_prog % 10
                memory[pt_num][0] = 0
                memory[pt_num][1] = 0
                i = 0

                frame_num_p = frame_num_prog * 10  # address where program is stored

                print("\ncur_pcb contents",cur_pcb.P)
                print("PCB id",cur_pcb.job_id)
                if(len(cur_pcb.P)!=0):
                    index= cur_pcb.P.pop(0)
                    memory[frame_num_p:frame_num_p+10] = drum[index:index+10]
                # print(drum[index:index+10])
                #display(memory,300)
                if(len(cur_pcb.P)!=0):
                    lq_am.insert(0,cur_pcb)
                else:
                    rq.append(cur_pcb)
            else:
                if(len(lq_am)!=0):
                    cur_pcb=lq_am.pop(0)
                    if(len(cur_pcb.P)!=0):
                        frame_num_prog = random.randint(0, 29)
                        while frame_num_prog in used_frames:  # finding unique frame
                            frame_num_prog = random.randint(0, 29)
                        used_frames.add(frame_num_prog)

                        pt_num = int(cur_pcb.PTR[1]) * 100 + int(cur_pcb.PTR[2]) * 10 + int(cur_pcb.PTR[3])
                        while(memory[pt_num][0]!='\0'):
                            pt_num+=1
                        
                        memory[pt_num][2] = frame_num_prog // 10
                        memory[pt_num][3] = frame_num_prog % 10
                        memory[pt_num][0] = 0
                        memory[pt_num][1] = 0

                        frame_num_p = frame_num_prog * 10
                        
                        index= cur_pcb.P.pop(0)
                        memory[frame_num_p:frame_num_p+10] = drum[index:index+10]
                        lq_am.insert(0,cur_pcb)
                    
                    if(len(cur_pcb.P)==0):
                        
                        lq_am.pop(0)
                        rq.append(cur_pcb)
                        mem_flag=False

        elif task == 'RD':
            pcb=ioq.pop(0)
            if(len(pcb.D)!=0):
                index=pcb.D.pop(0)
                memory[pcb.address:pcb.address+10]=drum[index:index+10]
                rq.append(pcb)
            else:
                pcb.error=1
                tq.append(pcb)        ##needs to be changed

        elif task == 'WT':
            pcb=ioq.pop(0)
            if(pcb.LLC< pcb.TLL):
                index=pcb.O.pop(0)
                drum[index:index+10]=memory[pcb.address:pcb.address+10]
                pcb.O.append(index)
                rq.append(pcb)
            else:
                pcb.error=2
                tq.append(pcb)
        start_channel(3)
        print("CH after ch3 in end",CH)

def master_mode():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, buffer_status
    if(len(rq) != 0):
        pcb = rq[0]
        #print("master mode")
        if (TI == 0 or TI == 1):
            if (SI == 0):
                if (PI == 1):
                    # Operation Code Error
                    rq[0].terminate_code = 4
                    tq.append(rq[0])
                    rq.pop()
                    memory = [['\0' for i in range(4)] for j in range(300)]
                    IR = [0 for i in range(4)]
                    
                    R = [0 for i in range(4)]
                    C = False

                elif (PI == 2):
                    # Operand Error
                    rq[0].terminate_code = 5
                    tq.append(rq[0])
                    rq.pop()
                    memory = [['\0' for i in range(4)] for j in range(300)]
                    IR = [0 for i in range(4)]
                    
                    R = [0 for i in range(4)]
                    C = False

                elif (PI == 3):  # page fault
                    print("valid page fault in master mode")
                    if (valid):  # valid argument passed to master mode function
                        valid_page_fault(pcb.PTR)
                        # rq.append(rq[0])              ##needs to be changed
                        # rq.pop()

                    else:
                        # invalid page fault
                        rq[0].terminate_code = 6
                        tq.append(rq[0])
                        rq.pop()
                        memory = [['\0' for i in range(4)] for j in range(300)]
                        IR = [0 for i in range(4)]
                        
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
                    rq.pop(0)
                    print("length of rq after halt",len(rq))
                    display(memory,300)
                    memory = [['\0' for i in range(4)] for j in range(300)]
                    IR = [0 for i in range(4)]
                    
                    R = [0 for i in range(4)]
                    C = False

        elif (TI == 2):
            rq[0].terminate_code = 3
            tq.append(rq[0])
            rq.pop()
            memory = [['\0' for i in range(4)] for j in range(300)]
            IR = [0 for i in range(4)]
            
            R = [0 for i in range(4)]
            C = False

    print("IOI in master mode", IOI)            ##needs to be changed or checked
    if IOI == 1:
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
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, buffer_status
    if(i == 1):
        IOI -= 1
        CH[0] = True
        CHT[0] = 0  # Channel Timer
    elif(i == 2):
        IOI -= 2
        CH[1] = True
        CHT[1] = 0

    elif(i == 3):
        IOI -= 4
        CH[2] = True
        CHT[2] = 0

    print("\n\n CH ",CH)

def simulate():
    global m, ch1, ch2, ch3, IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, buffer_status
    if(len(rq) != 0):
        pcb = rq[0]
        pcb.incrementTSC()
        if(pcb.TSC == TS):
            TI = 1
    # NEEDS TO BE REMOVED
    
    #print(CHT)
    #print(CHT_TOT)
    for i in range(3):
        if(CH[i]):
            CHT[i] += 1
            if(i == 0 and CHT[i] == CHT_TOT[i]):
                IOI += 1
                #CH[i] = False
                #CHT[i] = 0
            elif(i == 1 and CHT[i] == CHT_TOT[i]):
                IOI += 2
                #CH[i] = False
                #CHT[i] = 0
            elif(i == 2 and CHT[i] == CHT_TOT[i]):
                IOI += 4
                #CH[i] = False
                #CHT[i] = 0


def address_map(VA,PTR):
    global memory
    # first we get page table entry
    pte = (int(PTR[1]) * 100 + int(PTR[2]) * 10 + int(PTR[3])) + VA // 10

    if memory[pte][0] == '\0':  # checking if anything is present in page table entry
        return -1  # if not invoke page fault

    # calculate memory frame entry from pte
    addr = int(memory[pte][2]) * 10 + int(memory[pte][3])
    RA = addr * 10 + VA % 10  # calculate real address
    return RA


def valid_page_fault(PTR):
    print("PTR in valid page fault",PTR)
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

    print("current pointer in valid page fault",memory[c_ptr])


def execute_usrprgm():
    global m, ch1, ch2, ch3, task,IR, IC, R, C, SI, PI, TI, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH, valid, buffer_status
    print("in execute length of rq",len(rq))
    if len(rq) == 0:
        return
    time_counter = 0
    pcb = rq[0]    # get pcb of program to be executed
    print("pcb in execute user function",pcb)
    if (pcb.TTC <= pcb.TTL):   # checking for time limit exceeded error

        global  IR, R, C, T, SI, TI, PI, pd_error

        SI = 0
        PI = 0
        TI = 0
        # converting virtual address to real addresss
        inst_count = address_map(10 * pcb.curr_IC[0] + pcb.curr_IC[1],pcb.PTR) 
        if (inst_count == -1):  # master mode - operand error
            PI = 2
            return
        IR = memory[inst_count]
        print("IR", IR)
        pcb.curr_IC[1] += 1  # incrementing IC
        if pcb.curr_IC[1] == 10:
            pcb.curr_IC[0] += 1
            pcb.curr_IC[1] = 0
        inst = "" + IR[0] + IR[1]
        print("IC in execute user prog",pcb.curr_IC)
        if (inst[0] != "H"):

            if ((IR[2].isnumeric() and IR[3].isnumeric()) == False):  # checking for operand error

                PI = 2
                return
            real_address = address_map(int(IR[2]) * 10 + int(IR[3]),pcb.PTR)

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
                if pcb.curr_IC[1] != 0:
                    pcb.curr_IC[1] -= 1
                else:
                    pcb.curr_IC[1] = 9
                    pcb.curr_IC[0] -= 1
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
                pcb.curr_IC[0] = int(IR[2])
                pcb.curr_IC[1] = int(IR[3])

        elif inst == "GD":
            print("PTR IN GD",pcb.PTR)
            print("Real address in GN",real_address)
            if (real_address == -1):  # valid page fault
                PI = 3
                SI = 0
                print('valid page fault')
                
                valid = True
                if pcb.curr_IC[1] != 0:
                    pcb.curr_IC[1] -= 1
                else:
                    pcb.curr_IC[1] = 9
                    pcb.curr_IC[0] -= 1

                return

            SI = 1
            print("fun in GD")
            pcb.write=False
            pcb.read=True
            pcb.address=real_address
            ioq.append(pcb)
            rq.pop(0)
            task='RD'
            return
            # GD ERROR to be handled in master mode

        elif inst == "PD":
            if (real_address == -1):  # invalid page fault
                PI = 3
                valid = False
                return
            else:
                SI = 2
                pcb.read=False
                pcb.write=True
                pcb.address=real_address
                ioq.append(pcb)
                rq.pop(0)
                task='WT'
                return
                # PD ERROR TO BE HANDLED IN MASTER MODE
            #put_data(int(IR[2]) * 10 + int(IR[3]))

        elif inst == "H\0":
            SI = 3
            print("\t\tHalt occurred")
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
