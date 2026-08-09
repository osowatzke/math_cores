
DSP_A_WIDTH = 27
DSP_B_WIDTH = 18

MULT_A_WIDTH = 53 # Double
MULT_B_WIDTH = 53

MIN_WIDTH = min(DSP_A_WIDTH, DSP_B_WIDTH)

MAX_STAGES_A = (MULT_A_WIDTH + MIN_WIDTH - 1)//MIN_WIDTH
MAX_STAGES_B = (MULT_B_WIDTH + MIN_WIDTH - 1)//MIN_WIDTH

MAX_ITER_A = 2**MAX_STAGES_A

all_comb_a = []
for it in range(MAX_ITER_A):
    comb_a = []
    num_bits = MULT_A_WIDTH
    for stage in MAX_STAGES_A:
        if num_bits > 0:
            val = (it >> stage) & 1
            if val == 0
                num_bits -= MULT_A_WIDTH
            else:
                num_bits -= MULT_B_WIDTH
        else:
            val = -1
        comb_a.append(val)
    all_comb_a.append(comb_a)
    
all_comb_b = []
for it in range(MAX_ITER_A):
    comb_a = all_comb_a[it]
    for stage in MAX_STAGES_B:
        all_comb_b = comb_a[
        

for stage in range(MAX_STAGES_A):
    