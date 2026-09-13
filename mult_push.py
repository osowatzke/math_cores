DSP_A_WIDTH = 27
DSP_B_WIDTH = 18
DSP_P_WIDTH = 48

class FreeBits:
    def __init__(self, num_stages, config='26x17', off=0):
        self.free_bits  = []
        self.extra_bits = []
        self.off = off
        self.num_stages = num_stages
        self.config = config
        self.a_width = DSP_A_WIDTH - 1
        if   config == '26x17'  :
            self.__add_26x17_mults(num_stages)            
        elif config == '26x18L' :
            self.__add_26x17_mults(num_stages)
            self.__make_first_stage_x18()
        elif config == '26x18H' :
            self.__add_26x17_mults(num_stages)
            self.__make_last_stage_x18()
        elif config == '26x18LH':
            self.__add_26x17_mults(num_stages)
            self.__make_first_stage_x18()
            self.__make_last_stage_x18()
        elif config == '27x17'  :
            self.__add_27x17_mults(num_stages)
        elif config == '27x18L' :
            self.__add_27x17_mults(num_stages)
            self.__make_first_stage_x18()
        elif config == '27x18H' :
            self.__add_27x17_mults(num_stages)
            self.__make_last_stage_x18()
        elif config == '27x18LH':
            self.__add_27x17_mults(num_stages)
            self.__make_first_stage_x18()
            self.__make_last_stage_x18()
        else:
            raise ValueError('Unsupported config. Must be in (26|27)x(17|18L|18H|18LH)')
        
    def __add_26x17_mults(self, num_stages):
        self.free_bits = []
        s = 0
        for i in range(num_stages):
            for bit in range(s,s+DSP_P_WIDTH-1):
                if bit >= len(self.free_bits):
                    self.free_bits.append(1)
                else:
                    self.free_bits[bit] += 1
            s += (DSP_B_WIDTH - 1)
            
    def __add_27x17_mults(self, num_stages):
        self.__add_26x17_mults(num_stages)
        self.a_width = DSP_A_WIDTH
        s = DSP_A_WIDTH - 1
        for i in range(num_stages):
            for j in range(s,s+DSP_B_WIDTH-1):
                self.free_bits[j] -= 1
            s += 17
        
    def __make_first_stage_x18(self):
        self.extra_bits = [-1]
        for i in range(self.a_width - 1):
            self.free_bits[i] -= 1
    
    def __make_last_stage_x18(self):
        s = (self.num_stages - 1)*(DSP_B_WIDTH - 1)
        s += DSP_B_WIDTH - 1
        e = s + self.a_width
        for i in range(s,e):
            self.free_bits[i] -= 1
            
    def print(self):
        free_bits = self.extra_bits.copy()
        free_bits.extend(self.free_bits)
        off = self.off - len(self.extra_bits)
        
        s = 0
        old_val = 0
        for (i,v) in enumerate(free_bits):
            if ((i > 0) and (v != old_val)):
                e = i - 1
                print("%3d - %3d = %d" % (s+off,e+off,old_val))
                s = i
            old_val = v
        e = len(free_bits) - 1
        print("%3d - %3d = %d" % (s+off,e+off,old_val))
        
    def prod_width(self):
        if   self.config == '26x17'  :
            a_width = 26
            b_width = 17*self.num_stages
        elif self.config == '26x18L' :
            a_width = 26
            b_width = 17*self.num_stages + 1
        elif self.config == '26x18H' :
            a_width = 26
            b_width = 17*self.num_stages + 1
        elif self.config == '26x18LH':
            a_width = 26
            b_width = 17*self.num_stages + 2
        elif self.config == '27x17'  :
            a_width = 27
            b_width = 17*self.num_stages
        elif self.config == '27x18L' :
            a_width = 27
            b_width = 17*self.num_stages + 1
        elif self.config == '27x18H' :
            a_width = 27
            b_width = 17*self.num_stages + 1
        elif self.config == '27x18LH':
            a_width = 27
            b_width = 17*self.num_stages + 2
        return a_width + b_width
        
def combine(f1, f2):
    off1 = f1.off - len(f1.extra_bits)
    for i in range(off1, off1 + f1.prod_width()):
        if (i >= f2.off):
            bit = i - f2.off
            f2.free_bits[bit] -= 1
    off2 = f2.off - len(f2.extra_bits)
    s = off2 - f1.off
    f1.free_bits[s] -= 1
    f2.extra_bits = []
    s += 1
    for i in range(len(f2.free_bits)):
        if (f2.free_bits[i] >= 0):
            break
        else:
            f2.free_bits[i] += 1
            f1.free_bits[s] -= 1
        s += 1
    s = f2.off - f1.off
    for i in range(len(f1.free_bits)):
        v = f1.free_bits[i]
        if (i >= s and v < 0):
            f1.free_bits[i] -= v
            f2.free_bits[i-s] += v
    
def get_26x17_free_bits(num_stages):
    free_bits = []
    s = 0
    for i in range(num_stages):
        for bit in range(s,s+DSP_P_WIDTH-1):
            if bit >= len(free_bits):
                free_bits.append(1)
            else:
                free_bits[bit] += 1
        s += (DSP_B_WIDTH - 1)
    return free_bits

def get_26x18L_free_bits(num_stages):
    free_bits = get_26x17_free_bits(num_stages)
    for i in range(DSP_A_WIDTH-2):
        free_bits[i] -= 1
    return free_bits
    
def get_26x18H_free_bits(num_stages):
    free_bits = get_26x17_free_bits(num_stages)
    s = (num_stages - 1)*(DSP_B_WIDTH - 1)
    s += DSP_B_WIDTH - 1
    e = s + DSP_A_WIDTH - 1
    for i in range(s,e):
        free_bits[i] -= 1
    return free_bits
    
def get_26x18LH_free_bits(num_stages):
    free_bits = get_26x18H_free_bits(num_stages)
    for i in range(DSP_A_WIDTH-2):
        free_bits[i] -= 1
    return free_bits
    
def get_27x17_free_bits(num_stages):
    free_bits = get_26x17_free_bits(num_stages)
    s = DSP_A_WIDTH - 1
    for i in range(num_stages):
        for j in range(s,s+DSP_B_WIDTH-1):
            free_bits[j] -= 1
        s += 17
    return free_bits  
   
def get_27x18L_free_bits(num_stages):
    free_bits = get_27x17_free_bits(num_stages)
    for i in range(DSP_A_WIDTH-1):
        free_bits[i] -= 1
    return free_bits
    
def get_27x18H_free_bits(num_stages):
    free_bits = get_27x17_free_bits(num_stages)
    s = (num_stages - 1)*(DSP_B_WIDTH - 1)
    s += DSP_B_WIDTH - 1
    e = s + DSP_A_WIDTH
    for i in range(s,e):
        free_bits[i] -= 1
    return free_bits
    
def get_27x18LH_free_bits(num_stages):
    free_bits = get_27x18H_free_bits(num_stages)
    for i in range(DSP_A_WIDTH-1):
        free_bits[i] -= 1
    return free_bits
   
def print_range(free_bits, off=0):
    s = 0
    old_val = 0
    for (i,v) in enumerate(free_bits):
        if ((i > 0) and (v != old_val)):
            e = i - 1
            print("%3d - %3d = %d" % (s+off,e+off,old_val))
            s = i
        old_val = v
    e = len(free_bits) - 1
    print("%3d - %3d = %d" % (s+off,e+off,old_val))
    
# Double Precision
a_width = 53
b_width = 53

#  0 - 25 # a1*b1 [0-25]*0
#  1 - 43 # a1*b2 [0-25]*[1-17]
# 26      # a2*b1 26*0
# 27 - 43 # a2*b2 26*[1-17]

#  0 - 41 # a1*b1 [0-25]*[0-16]
# 26 - 42 # a2*b1 26*[0-16]
# 17 - 42 # a1*b2 [0-25]*17
# 43      # a2*b2 26*17

# 27*18 - 27*17 - 27*18
'''
free_bits = []
num_stages = 3
s = 0
for i in range(num_stages):
    for bit in range(s,s+DSP_P_WIDTH-1):
        if bit >= len(free_bits):
            free_bits.append(1)
        else:
            free_bits[bit] += 1
    s += (DSP_B_WIDTH - 1)
'''

num_stages = 3
config = ['26x17','26x18L','26x18H','26x18LH','27x17','27x18L','27x18H','27x18LH']

for i in range(len(config)):
    free_bits = FreeBits(num_stages, config[i])
    print("%s free bits:" % config[i])
    free_bits.print()
    print("\n")
    
f1 = FreeBits(3, '27x18LH', off=0)
f2 = FreeBits(3, '27x18LH', off=27)
f3 = FreeBits(4, '26x18LH', off=54)

'''
print("F1:")
f1.print()
print("\n")

print("F2:")
f2.print()
print("\n")
'''
combine(f1,f2)

print("F1:")
f1.print()
print("\n")

print("F2:")
f2.print()
print("\n")

'''
combine(f2,f3)

print("F2:")
f2.print()
print("\n")

print("F3:")
f3.print()
print("\n")
'''

'''
free_bits = get_26x18L_free_bits(num_stages)
print("26x18L free bits:")
print_range(free_bits)
print("\n")

free_bits = get_26x18H_free_bits(num_stages)
print("26x18H free bits:")
print_range(free_bits)
print("\n")

free_bits = get_26x18LH_free_bits(num_stages)
print("26x18LH free bits:")
print_range(free_bits)
print("\n")

free_bits = get_27x17_free_bits(num_stages)
print("27x17 free bits:")
print_range(free_bits)
print("\n")

free_bits = get_27x18L_free_bits(num_stages)
print("27x18L free bits:")
print_range(free_bits)
print("\n")

free_bits = get_27x18H_free_bits(num_stages)
print("27x18H free bits:")
print_range(free_bits)
print("\n")

free_bits = get_27x18LH_free_bits(num_stages)
print("27x18LH free bits:")
print_range(free_bits)
print("\n")
'''
'''
for i in range(DSP_A_WIDTH-1):
    free_bits[i] -= 1
    
print("Free range stage 0:")
print_range(free_bits)
print("\n")

for i in range(DSP_A_WIDTH-1,DSP_A_WIDTH+DSP_B_WIDTH-2):
    free_bits[i] -= 1

print("Free range stage 0:")
print_range(free_bits)
print("\n")

s = 17 + DSP_A_WIDTH - 1
for i in range(1,num_stages):
    for j in range(s,s+DSP_B_WIDTH-1):
        free_bits[j] -= 1
    s += 17
    
print("Free range stage 0:")
print_range(free_bits)
print("\n")

s = (num_stages-1)*17+DSP_B_WIDTH-1
for i in range(s,s+DSP_A_WIDTH):
    free_bits[i] -= 1
    
print("Free range stage 0:")
print_range(free_bits)
print("\n")

free_bits[0]


DSP_B_WIDTH

def num_b_stages(width):
    return ((width - 2) + DSP_B_WIDTH - 1)//DSP_B_WIDTH
    
def num_a_stages(width):
    return ((

b_stages = ((b_width - 2) + DSP_B_WIDTH - 1)// DSP_B_WIDTH
a_stages = 
'''
