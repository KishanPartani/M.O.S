def begin():
    global m,ch1,ch2,ch3, IR, IC, R, C, SI, PI, TI, PTR, used_frames, memory, opfile, input_buffer, data_index, pd_error, gd_error, supervisory_storage, drum, TS, TSC, CH, ebq, ifbq, ofbq, rq, ioq, lq, tq, IOI, CHT, CH
    m = 0
    IR = [0 for i in range(4)]
    IC = [0 for i in range(2)]
    R = [0 for i in range(4)]
    C = False
    SI = 0
    PI = 0
    TI = 0
    TS = 0
    ch1 = 5   #needs to be checked
    ch2 = 2   #needs to be checked
    ch3 = 3   #needs to be checked
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
    pd_error = 0   # for line limit exceeded
    gd_error = 0   # for out of data
    IOI = 0
    start_channel(1)

class PCB:
    def __init__(self, job_id, ttl, tll, ttc, llc,tsc):
        self.job_id = job_id
        self.TTL = ttl   # total time limit
        self.TTC = ttc   # total time counter
        self.TLL = tll   # total line limit
        self.LLC = llc   # line limit counter
        self.TSC = tsc   #time slice counter

    #
    #need to store count for data card and program card
    #
    #starting address of data card and program card
    #
    #starting address of op line
    def incrementLLC(self):
        self.LLC = self.LLC + 1

    def incrementTTC(self):
        self.TTC = self.TTC + 1

    def incrementTSC(self):
        self.TSC = self.TSC + 1


def start_channel(i):
    global IOI, CH, CHT
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

def simulation():
    #
    #obj needs to be changed later with the PCB object
    obj=PCB()
    obj.incrementTTC()
    global TI,TS,CH,ch1,ch2,ch3,IOI
    if(obj.TTC==obj.TTL):
        TI=2
        master_mode()
    
    obj.incrementTSC()
    if(obj.TSC==TS):
        TI=1
        master_mode()

    for i in range(3):
        if(CH[i]):
            CHT[i] += 1
            if(i==0 and CHT[i]==ch1):
                IOI += 1
            elif(i==1 and CHT[i]==ch2):
                IOI += 2
            elif(i==2 and CHT[i]==ch3):
                IOI += 4
            master_mode()
    


if __name__ == '__main__':
    begin()
