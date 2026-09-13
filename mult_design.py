class DspSlice:
    def __init__(self, config='26x17'):
        self.c_bits = [1]*46
        self.virtual_bits = []
        self.config = config
        if config=='27x18L':
            self.make_27x18L_mult()
        elif config=='27x18H':
            self.make_27x18H_mult()
        elif config=='27x17':
            self.make_27x17_mult()
        elif config=='26x18L':
            self.make_26x18L_mult()
        elif config=='26x18H':
            self.make_26x18H_mult()
        elif config=='26x17':
            self.make_26x17_mult()
        else:
            raise ValueError(f"Unsupported Config '{config}'")
            
    def make_27x18L_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = [-1]
        for i in range(26):
            self.c_bits[i] -= 1
        for i in range(26, 26+17):
            self.c_bits[i] -= 1
            
    def make_27x18H_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = []
        for i in range(17, 17+27):
            self.c_bits[i] -= 1
        for i in range(26, 26+17):
            self.c_bits[i] -= 1
            
    def make_27x17_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = []
        for i in range(26, 26+17):
            self.c_bits[i] -= 1
            
    def make_26x18L_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = [-1]
        for i in range(25):
            self.c_bits[i] -= 1
            
    def make_26x18H_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = []
        for i in range(17, 17+26):
            self.c_bits[i] -= 1
            
    def make_26x17_mult(self):
        self.c_bits = [1]*46
        self.virtual_bits = []
            
            
class DspSliceArray:
    def __init__(self):
        self.slices = []
        self.prod_width = []
        self.off = [0]
        
    def add_row(self, num_slices, config='26x17'):
        row = []
        b_width = 0
        for i in range(num_slices):
            if i == 0:
                if (config=='27x18LH') or (config=='27x18L'):
                    row.append(DspSlice('27x18L'))
                    b_width += 18
                elif (config=='27x18H') and (num_slices==1):
                    row.append(DspSlice('27x18H'))
                    b_width += 18
                elif (config=='26x18LH') or (config=='26x18L'):
                    row.append(DspSlice('26x18L'))
                    b_width += 18
                elif (config=='26x18H') and (num_slices==1):
                    row.append(DspSlice('26x18H'))
                    b_width += 18
                elif config.startswith('27x'):
                    row.append(DspSlice('27x17'))
                    b_width += 17
                else:
                    row.append(DspSlice('26x17'))
                    b_width += 17
            elif i == (num_slices-1):
                if (config=='27x18LH') or (config=='27x18H'):
                    row.append(DspSlice('27x18H'))
                    b_width += 18
                elif (config=='26x18LH') or (config=='26x18H'):
                    row.append(DspSlice('26x18H'))
                    b_width += 18
                elif config.startswith('27x'):
                    row.append(DspSlice('27x17'))
                    b_width += 17
                else:
                    row.append(DspSlice('26x17'))
                    b_width += 17
            else:
                if config.startswith('27x'):
                    row.append(DspSlice('27x17'))
                    b_width += 17
                else:
                    row.append(DspSlice('26x17'))
                    b_width += 17
        self.slices.append(row)
        if config.startswith('27x'):
            self.off.append(self.off[-1] + 27)
            a_width = 27
        else:
            self.off.append(self.off[-1] + 26)
            a_width = 26
        self.prod_width.append(a_width + b_width)      
                
    def get_c_bits(self):
        virtual_bits = []
        c_bits = []
        last_off = 0
        has_virtual_bit = False
        for (ridx,row) in enumerate(self.slices):
            off = self.off[ridx]
            if ridx > 0:
                width = self.prod_width[ridx-1]
                if has_virtual_bit:
                    width -= 1
                for i in range(off, last_off+width):
                    if i < len(c_bits):
                        c_bits[i] -= 1
                    else:
                        c_bits.append(-1)
            last_off = off                
            for (sidx,s) in enumerate(row):
                if ridx == 0 and sidx == 0:
                    virtual_bits = s.virtual_bits
                elif len(s.virtual_bits) > 0:
                    c_bits[off-1] -= 1
                if sidx == 0 and len(s.virtual_bits) > 0:
                    has_virtual_bit = True
                i = off
                for bit in s.c_bits:
                    if i < len(c_bits):
                        c_bits[i] += bit
                    else:
                        c_bits.append(bit)
                    i += 1
                off += 17
        return (c_bits, virtual_bits)
        
    def is_possible(self):
        c_bits = self.get_c_bits()[0]
        possible = True
        for bit in c_bits:
            if bit < 0:
                possible = False
        return possible        
        
    def print_c_bits(self):
        (c_bits, virtual_bits) = self.get_c_bits()
        s = 0
        last = None
        if len(virtual_bits) > 0:
            s = -1
            last = -1
        for (idx,bit) in enumerate(c_bits):
            if last is None:
                s = 0
                last = bit
            if bit != last:
                e = idx - 1
                print('%3d - %3d: %d' % (s,e,last))
                s = idx
                last = bit
        e = idx
        print('%3d - %3d: %d' % (s,e,last))
            
array = DspSliceArray()
array.add_row(5, '27x18LH')
array.add_row(5, '27x18LH')
array.add_row(5, '27x18LH')
array.add_row(5, '27x18LH')
array.add_row(5, '26x18LH')
array.print_c_bits()
        
    