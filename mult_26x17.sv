`include "dsp48e2_params.vh"
`timescale 1 ns/1 ns    
module mult_26x17 #(
    parameter   USE_CIN  = 0,
    parameter   USE_PCIN = 0) (
    input  wire clkIn,
    input  wire rstIn,
    input  wire enIn = 1'b1,
    input  wire [25:0] aIn,
    input  wire [16:0] bIn,
    input  wire [47:0] cIn = 48'b0,
    input  wire [47:0] pCIn = 48'b0,
    output wire [47:0] pOut,
    output wire [47:0] pCOut);
    
    wire [29:0] a;
    wire [17:0] b;
    
    assign a = {4'b0, aIn};
    assign b = {1'b0, bIn};
    
    localparam [1:0] W = USE_CIN  ? `W_C          : `W_0;
    localparam [2:0] Z = USE_PCIN ? `Z_PCIN_SHIFT : `Z_0;
    localparam [8:0] OPMODE = `OPMODE(W, `X_M, `Y_M, Z);
    
    DSP48E2 #(
        // Feature Control Attributes: Data Path Selection
        .AMULTSEL("A"),                    // Selects A input to multiplier (A, AD)
        .A_INPUT("DIRECT"),                // Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
        .BMULTSEL("B"),                    // Selects B input to multiplier (AD, B)
        .B_INPUT("DIRECT"),                // Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
        .PREADDINSEL("A"),                 // Selects input to pre-adder (A, B)
        .RND(48'h000000000000),            // Rounding Constant
        .USE_MULT("MULTIPLY"),             // Select multiplier usage (DYNAMIC, MULTIPLY, NONE)
        .USE_SIMD("ONE48"),                // SIMD selection (FOUR12, ONE48, TWO24)
        .USE_WIDEXOR("FALSE"),             // Use the Wide XOR function (FALSE, TRUE)
        .XORSIMD("XOR24_48_96"),           // Mode of operation for the Wide XOR (XOR12, XOR24_48_96)
        // Pattern Detector Attributes: Pattern Detection Configuration
        .AUTORESET_PATDET("NO_RESET"),     // NO_RESET, RESET_MATCH, RESET_NOT_MATCH
        .AUTORESET_PRIORITY("RESET"),      // Priority of AUTORESET vs. CEP (CEP, RESET).
        .MASK(48'h3fffffffffff),           // 48-bit mask value for pattern detect (1=ignore)
        .PATTERN(48'h000000000000),        // 48-bit pattern match for pattern detect
        .SEL_MASK("MASK"),                 // C, MASK, ROUNDING_MODE1, ROUNDING_MODE2
        .SEL_PATTERN("PATTERN"),           // Select pattern value (C, PATTERN)
        .USE_PATTERN_DETECT("NO_PATDET"),  // Enable pattern detect (NO_PATDET, PATDET)
        // Programmable Inversion Attributes: Specifies built-in programmable inversion on specific pins
        .IS_ALUMODE_INVERTED(4'b0000),     // Optional inversion for ALUMODE
        .IS_CARRYIN_INVERTED(1'b0),        // Optional inversion for CARRYIN
        .IS_CLK_INVERTED(1'b0),            // Optional inversion for CLK
        .IS_INMODE_INVERTED(5'b00000),     // Optional inversion for INMODE
        .IS_OPMODE_INVERTED(9'b000000000), // Optional inversion for OPMODE
        .IS_RSTALLCARRYIN_INVERTED(1'b0),  // Optional inversion for RSTALLCARRYIN
        .IS_RSTALUMODE_INVERTED(1'b0),     // Optional inversion for RSTALUMODE
        .IS_RSTA_INVERTED(1'b0),           // Optional inversion for RSTA
        .IS_RSTB_INVERTED(1'b0),           // Optional inversion for RSTB
        .IS_RSTCTRL_INVERTED(1'b0),        // Optional inversion for RSTCTRL
        .IS_RSTC_INVERTED(1'b0),           // Optional inversion for RSTC
        .IS_RSTD_INVERTED(1'b0),           // Optional inversion for RSTD
        .IS_RSTINMODE_INVERTED(1'b0),      // Optional inversion for RSTINMODE
        .IS_RSTM_INVERTED(1'b0),           // Optional inversion for RSTM
        .IS_RSTP_INVERTED(1'b0),           // Optional inversion for RSTP
        // Register Control Attributes: Pipeline Register Configuration
        .ACASCREG(1),                      // Number of pipeline stages between A/ACIN and ACOUT (0-2)
        .ADREG(1),                         // Pipeline stages for pre-adder (0-1)
        .ALUMODEREG(1),                    // Pipeline stages for ALUMODE (0-1)
        .AREG(1),                          // Pipeline stages for A (0-2)
        .BCASCREG(1),                      // Number of pipeline stages between B/BCIN and BCOUT (0-2)
        .BREG(1),                          // Pipeline stages for B (0-2)
        .CARRYINREG(1),                    // Pipeline stages for CARRYIN (0-1)
        .CARRYINSELREG(1),                 // Pipeline stages for CARRYINSEL (0-1)
        .CREG(1),                          // Pipeline stages for C (0-1)
        .DREG(1),                          // Pipeline stages for D (0-1)
        .INMODEREG(1),                     // Pipeline stages for INMODE (0-1)
        .MREG(1),                          // Multiplier pipeline stages (0-1)
        .OPMODEREG(1),                     // Pipeline stages for OPMODE (0-1)
        .PREG(1)                           // Number of pipeline stages for P (0-1)
    )
    DSP48E2_inst (
        .PCOUT(pCOut),                   // 48-bit output: Cascade output
        .P(pOut),                        // 48-bit output: Primary data
        // Cascade inputs: Cascade Ports
        .ACIN(30'b0),                    // 30-bit input: A cascade data
        .BCIN(18'b0),                    // 18-bit input: B cascade
        .CARRYCASCIN(1'b0),              // 1-bit input: Cascade carry
        .MULTSIGNIN(1'b0),               // 1-bit input: Multiplier sign cascade
        .PCIN(pCIn),                     // 48-bit input: P cascade
        // Control inputs: Control Inputs/Status Bits
        .ALUMODE(4'b0),                  // 4-bit input: ALU control (Z + W + X + Y + CIN)
        .CARRYINSEL(3'b0),               // 3-bit input: Carry select (CARRYIN)
        .CLK(clkIn),                     // 1-bit input: Clock
        .INMODE(5'b10001),               // 5-bit input: INMODE control (B1, X, Pre-Add D Input = 0, A*B, A1)
        .OPMODE(OPMODE),                 // 9-bit input: Operation mode (Y=M, X=M)
        // Data inputs: Data Ports
        .A(a),                           // 30-bit input: A data
        .B(b),                           // 18-bit input: B data
        .C(cIn),                         // 48-bit input: C data
        .CARRYIN(1'b0),                  // 1-bit input: Carry-in
        .D(27'b0),                       // 27-bit input: D data
        // Reset/Clock Enable inputs: Reset/Clock Enable Inputs
        .CEA1(enIn),                     // 1-bit input: Clock enable for 1st stage AREG
        .CEA2(1'b0),                     // 1-bit input: Clock enable for 2nd stage AREG
        .CEAD(1'b0),                     // 1-bit input: Clock enable for ADREG
        .CEALUMODE(enIn),                // 1-bit input: Clock enable for ALUMODE
        .CEB1(enIn),                     // 1-bit input: Clock enable for 1st stage BREG
        .CEB2(1'b0),                     // 1-bit input: Clock enable for 2nd stage BREG
        .CEC(enIn),                      // 1-bit input: Clock enable for CREG
        .CECARRYIN(1'b0),                // 1-bit input: Clock enable for CARRYINREG
        .CECTRL(enIn),                   // 1-bit input: Clock enable for OPMODEREG and CARRYINSELREG
        .CED(1'b0),                      // 1-bit input: Clock enable for DREG
        .CEINMODE(enIn),                 // 1-bit input: Clock enable for INMODEREG
        .CEM(enIn),                      // 1-bit input: Clock enable for MREG
        .CEP(enIn),                      // 1-bit input: Clock enable for PREG
        .RSTA(rstIn),                    // 1-bit input: Reset for AREG
        .RSTALLCARRYIN(1'b0),            // 1-bit input: Reset for CARRYINREG
        .RSTALUMODE(rstIn),              // 1-bit input: Reset for ALUMODEREG
        .RSTB(rstIn),                    // 1-bit input: Reset for BREG
        .RSTC(rstIn),                    // 1-bit input: Reset for CREG
        .RSTCTRL(rstIn),                 // 1-bit input: Reset for OPMODEREG and CARRYINSELREG
        .RSTD(1'b0),                     // 1-bit input: Reset for DREG and ADREG
        .RSTINMODE(rstIn),               // 1-bit input: Reset for INMODEREG
        .RSTM(rstIn),                    // 1-bit input: Reset for MREG
        .RSTP(rstIn)                     // 1-bit input: Reset for PREG
    );

endmodule