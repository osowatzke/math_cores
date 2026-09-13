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
        
    def create_xml_file(self):
        with open('test.drawio','w') as file:
            file.write('<mxfile host="app.diagrams.net" pages="1">\n')
            file.write('  <diagram name="Page-1">\n')
            file.write('    <mxGraphModel dx="871" dy="500" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">\n')
            file.write('      <root>\n')
            file.write('        <mxCell id="0" />\n')
            file.write('        <mxCell id="1" parent="0" />\n')
            xi = 850 - 80
            y = 80
            for i in range(len(self.slices)):
                row = self.slices[i]
                off = self.off[i]
                for (j,s) in enumerate(row):
                    h = 20
                    if s.config == '27x18L':
                        rects = [[off, 27], [off+1, 43], [off+27, 17]]
                        off += 18
                    elif s.config == '27x18H':
                        rects = [[off, 43], [off+17, 27], [off+26, 17]]
                        off += 18
                    elif s.config == '27x17':
                        rects = [[off, 43], [off+26, 17]]
                        off += 17
                    elif s.config == '26x18L':
                        rects = [[off, 26], [off+1, 43]]
                        off += 18
                    elif s.config == '26x18H':
                        rects = [[off, 43], [off+26, 17]]
                        off += 18
                    elif s.config == '26x17':
                        rects = [[off, 43]]
                        off += 17
                    else:
                        raise ValueError(f"Unsupported Config '{s.config}'")
                    for rect in rects:
                        x = xi - rect[0]*4
                        w = rect[1]*4
                        s = rect[0]
                        e = rect[0] + rect[1] - 1
                        file.write(f'        <mxCell id="rect{i}-{j}" parent="1" style="rounded=0;whiteSpace=wrap;html=1;" value="" vertex="1">\n')
                        file.write(f'          <mxGeometry height="{h}" width="{w}" x="{x-w}" y="{y}" as="geometry" />\n')
                        file.write('        </mxCell>\n')
                        file.write(f'        <mxCell id="s{i}-{j}" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;rounded=0;" value="{s}" vertex="1">')
                        file.write(f'          <mxGeometry height="20" width="40" x="{x-40}" y="{y+20}" as="geometry" />\n')
                        file.write('        </mxCell>\n')
                        file.write(f'        <mxCell id="e{i}-{j}" parent="1" style="text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;rounded=0;" value="{e}" vertex="1">')
                        file.write(f'          <mxGeometry height="20" width="40" x="{x-w}" y="{y+20}" as="geometry" />\n')
                        file.write('        </mxCell>\n')                        
                        y += 40
            file.write('      </root>\n')
            file.write('    </mxGraphModel>\n')
            file.write('  </diagram>\n')
            file.write('</mxfile>')
            
array = DspSliceArray()
array.add_row(3, '27x18LH')
array.add_row(3, '26x18LH')
array.print_c_bits()
array.create_xml_file()


    