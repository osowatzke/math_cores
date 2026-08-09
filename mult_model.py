import numpy as np

DSP_MIN_WIDTH = 18

def mult(a,b,a_width,b_width):
    if b_width > a_width:
        a, b = b, a
        a_width, b_width = b_width, a_width
        
    a_terms = (a_width + DSP_MIN_WIDTH - 1)//DSP_MIN_WIDTH
    b_terms = (b_width + DSP_MIN_WIDTH - 1)//DSP_MIN_WIDTH
    num_cols = a_terms + b_terms - 1
    num_rows = b_terms
    
    a = np.int64(a).view(np.uint64)
    b = np.int64(b).view(np.uint64)
    cell_mask = np.uint64(2**DSP_MIN_WIDTH - 1)
    
    s_col = np.zeros(num_cols, dtype=np.uint64)
    for col in range(num_cols):
        for row in range(num_rows):
            if (row <= col) and (col < (row + a_terms)):
                a_off = np.uint64((col - row)*DSP_MIN_WIDTH)
                b_off = np.uint64(row*DSP_MIN_WIDTH)
                a_cell = (a >> a_off) & cell_mask
                b_cell = (b >> b_off) & cell_mask
                s_col[col] += a_cell * b_cell
        if col < (num_cols - 1):
            s_col[col+1] = s_col[col] >> np.uint64(DSP_MIN_WIDTH)
            s_col[col] = s_col[col] & cell_mask
    
    s = np.uint64(0)
    for col in range(num_cols):
        s += s_col[col] << np.uint64(col*DSP_MIN_WIDTH)
    
    return s


def mult2(a,b):
    DSP_B_MASK = 2**17 - 1
    DSP_A_MASK = 2**26 - 1
    DSP_C_MASK = 2**47 - 1
    
    b1 = (b >>  0) & 1
    b2 = (b >>  1) & DSP_B_MASK
    b3 = (b >> 18) & DSP_B_MASK
    b4 = (b >> 35) & DSP_B_MASK
    b5 = (b >> 52) & 1
    
    a1 = (a >>  0) & DSP_A_MASK
    a2 = (a >> 26) & 1
    a3 = (a >> 27) & DSP_A_MASK
    
    m1 = a1*b2
    m2 = a1*b3
    m3 = a1*b4
    m4 = a3*b2
    m5 = a3*b3
    m6 = a3*b4
    
    c1 = a*b1
    c2 = a2*((b4 << 34) | (b3 << 17) | b2)
    c3 = a*b5
    
    r = c1 + (m1 << 1) + (m2 << 18) + (c2 << 27) + (m4 << 28) + (m3 << 35) + (m5 << 45) + (c3 << 52) + (m6 << 62)

    p3 = c1 + (m1 << 1) + (m2 << 18) + (c2 << 27) + (m3 << 35)
    p2 = c1 + (m1 << 1) + (m2 << 18)
    p5 = c1 + (m1 << 1) + (m2 << 18) + (c2 << 27) + (m4 << 28) + (m3 << 35) + (m5 << 45) + ((c3 & (2**10-1)) << 52)
    
    r1 = c1 & 1 # 0
    c1 >>= 1
    p1 = m1 + (c1 & (2**43 - 1))
    r2 = p1 & (2**17 - 1) # 1 - 17
    c1 >>= 43
    p2 = m2 + (p1 >> 17) + ((c2 & (2**17 - 1)) << 9) + ((c1 & (2**9 - 1)) << 26)
    r3 = p2 & (2**10 - 1) # 18 - 27
    c2 >>= 17
    p3 = m3 + (p2 >> 17) + ((c2 & (2**34 - 1)) << 9)
    p4 = m4 + ((p2 >> 10) & (2**7 - 1)) + ((p3 & (2**10 - 1)) << 7) + ((c3 & (2**10 - 1)) << 24)
    c3 >>= 10
    r4 = p4 & (2**17 - 1) # 28 - 44
    p5 = m5 + (p4 >> 17) + (p3 >> 10)
    r5 = p5 & (2**17 - 1) # 45 - 61
    p6 = m6 + (p5 >> 17) + c3
    r6 = p6 # 62 - 105
    
    r = (r6 << 62) | (r5 << 45) | (r4 << 28) | (r3 << 18) | (r2 << 1) | r1
    
    return r
    
    '''
    r1 = c1 & 1 # 0
    p1 = m1 + (c1 >> 1) & (2**46 - 1) # 1 - 46
    r2 = p1 & (2**17 - 1) 
    p2 = m2 + (p1 >> 17) + (c1 >> 47) & (2**6 - 1) + ((c2 & (2**8 - 1)) << 9) # 47-52, 27-34
    r3 = p2 & (2**10 - 1)
    p3 = m3 + (p2 >> 17) + (c2 >> 8) & (2**51 - 1) # 35-77
    p4 = m4 + (p2 >> 10) & (2**7 - 1) + ((p3 & (2**39 - 1)) << 7)
    r4 = p4 && (2**7 - 1)
    p5 = m5 + (p4 >> 17) + ((c3 & (2**10-1)) << 7) + (((p3 >> 39) & (2**4 - 1)) << 29)
    
    m1 = b2*a1
    p1 = m1
    m2 = b3*a1
    p2 = m2 + (p1 >> 17)
    m3 = b4*a1
    p3 = m3 + (p2 >> 17)
    
    if b1 == 1:
       m1 + a1  

'''     
'''  
class LongNumber:
    def __init__(self, val, width):
        if isinstance(val, np.array):
            self.__val = val
            self.__width = width
        else:
            num_chars = (width + 7)//8
            self.__val = np.zeros(num_chars, dtype=np.uint8)
            for char in range(num_chars):
                self.__val[char] = np.uint8((np.uint64(val) >> np.uint64(char*8)) & np.uint64(2**8 - 1))
            self.__width = width
            
    def __add__(self, other):
        width = max(self.__width, other.__width) + 1
        num_chars = (width + 7)//8
        val = np.zeros(num_chars, dtype=np.uint8)
        a = np.concatenate((self.__val, np.zeros(num_chars - len(self.__val), dtype=np.uint8)))
        b = np.concatenate((other.__val, np.zeros(num_chars - len(other.__val), dtype=np.uint8)))
        c = np.int32(0)
        for char in range(num_chars):
            y = np.int32(a[char]) + np.int32(b[char]) + c
            c = y >> np.int32(2**8 - 1)
            val[char] = np.uint8(y & np.int32(2**8 - 1))
        return LongNumber(val, width)
        
    def __lshift__(self, other)
        
        
    def __mult__(self, other):
        width = self.__width + other.__width
        num_chars = (width + 7)//8
        val = np.zeros(num_chars, dtype=np.uint8)
        a = np.concatenate((self.__val, np.zeros(num_chars - len(self.__val), dtype=np.uint8)))
        b = np.concatenate((other.__val, np.zeros(num_chars - len(other.__val), dtype=np.uint8)))
        c = np.uint64(0)
        for char in range(num_chars):
            x = np.uint64(a[char])*np.uint64(b[char]) + c
            y = (x & np.uint64(2**32 - 1)) + (c & np.uint64(2**32 - 1))
            val[word] = y & np.uint64(2**32 - 1)
            c = (y >> np.uint64(32)) + (x >> np.uint64(32)) + (c >> np.uint64(32))
        return LongNumber(val, width)
        
    def __repr__(self):
        
            
            
        
        
def long_mult(a,b,a_width,b_width)    
    a = np.uint64(a)
    b = np.uint64(b)
    r = zeros(2,dtype=np.uint64)
    mask = np.uint64(2**32 - 1)
    a_lsb = a & mask
    a_msb = (a >> 32) & mask
    b_lsb = b & mask
    b_msb = (b >> 32) & mask
    r[1] = a_lsb * b_lsb
    r[2] = b_lsb * b_msb
'''
    
def mult3(a,b):
    DSP_A_WIDTH = 26
    DSP_B_WIDTH = 17
    
    DSP_A_MASK = (2**DSP_A_WIDTH - 1)
    DSP_B_MASK = (2**DSP_B_WIDTH - 1)
    
    a1 = (a >>  0) & DSP_A_MASK #  0 - 25
    a2 = (a >> 26) & 1          # 26
    a3 = (a >> 27) & DSP_A_MASK # 27 - 52
    
    b1 = (b >>  0) & 1          #  0
    b2 = (b >>  1) & DSP_B_MASK #  1 - 17
    b3 = (b >> 18) & DSP_B_MASK # 18 - 34
    b4 = (b >> 35) & DSP_B_MASK # 35 - 51
    b5 = (b >> 52) & 1          # 52
    
    m1 = a1 * b2
    
    c1 = a1 * b1 #  0 - 25
    c2 = a2 * b1 # 26 
    c3 = a2 * b2 # 27 - 43
    
    r1 = c1 & 1 # 0
    p1 = m1 + ((c1 >> 1) | (c2 << 25) | (c3 << 26)) # 1+
    r2 = p1 & (2**17 - 1) # 1 - 17
    
    m2 = a1 * b3
    
    c4 = a2 * b3 # 44 - 60
    
    c8 = b1 * a3 # 27 - 52
    
    p2 = m2 + (p1 >> 17) + (((c8 & (2**8 - 1)) << 9) | (c4 << 26)) # 18+   
    r3 = p2 & (2**10 - 1) # 18 - 27
    
    m3 = a1 * b4
    
    c5 = a1 * b5 # 52 - 77
    c6 = a2 * b5 # 78
    c7 = a2 * b4 # 61 - 77
    
    p3 = m3 + (p2 >> 17) + (((c8 >> 8) & (2**10 - 1)) | (c5 << 17) | (c6 << 43)) # 35+
    
    m4 = a3 * b2
    
    # c8 = b1 * a3 # 27 - 52
    
    p4 = m4 + (((p2 >> 10) & (2**7 - 1)) | ((p3 & (2**10 - 1)) << 7) | ((c8 >> 18) << 17) | ((c7 & 1) << 33)) # 28+
    r4 = p4 & (2**17 - 1) # 28 - 44
    
    m5 = a3 * b3
    
    p5 = m5 + (p4 >> 17) + (p3 >> 10) # 45+
    r5 = p5 & (2**17 - 1) # 45 - 61
    
    m6 = a3 * b4
    c9 = a3 * b5 # 79 - 104
    
    p6 = m6 + (p5 >> 17) + ((c7 >> 1) | (c9 << 17)) # 62+
    r6 = p6
    
    r = r1 | (r2 << 1) | (r3 << 18) | (r4 << 28) | (r5 << 45) | (r6 << 62)
    
    return r
    
    
x = 2**53 - 1
y = 2**53 - 1

np.random.seed(0)

N = 10000
for i in range(N):
    x = int(np.random.randint(0,2**53-1,dtype=np.uint64))
    y = int(np.random.randint(0,2**53-1,dtype=np.uint64))
    z1 = x*y
    z2 = mult3(x,y)
    if (z1 != z2):
        print(z1)
        print(z2)
        raise Exception('Mismatch in Multiplier Output')
        
print('All checks passed!')   
    
    
# 262144
# x, y = 262144+84184,267980
# print(mult(x,y,24,24))
# print(x*y)
    