`ifndef DSP48E2_PARAMS_VH
`define DSP48E2_PARAMS_VH

`define W_0          2'b00
`define W_P          2'b01
`define W_RND        2'b10
`define W_C          2'b11

`define X_0          2'b00
`define X_M          2'b01
`define X_P          2'b10
`define X_AB         2'b11

`define Y_0          2'b00
`define Y_M          2'b01
`define Y_ONES       2'b10
`define Y_C          2'b11

`define Z_0          3'b000
`define Z_PCIN       3'b001
`define Z_P          3'b010
`define Z_C          3'b011
`define Z_P_MACC_EXT 3'b100
`define Z_PCIN_SHIFT 3'b101
`define Z_P_SHIFT    3'b110

`define OPMODE(W, X, Y, Z) {W, Z, Y, X}

`endif