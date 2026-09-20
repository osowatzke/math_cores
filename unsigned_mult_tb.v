`timescale 1 ns/1 ns

module unsigned_mult_tb;

    parameter CLK_PERIOD = 10;
    parameter RESET_TIME = 100;
    
    reg clk;
    reg rst;
    
    initial begin
        clk <= 0;
        rst <= 1;
        #RESET_TIME;
        rst <= 0;
    end
    
    always #(CLK_PERIOD/2) clk = ~clk;
    
    reg [31:0] aR;
    reg [31:0] bR;
    
    always @(posedge clk) begin
        if (rst == 1) begin
            aR  <= 0;
            bR  <= 0;
        end else begin
            aR  <= $random;
            bR  <= $random;
        end
    end
    
    wire [63:0] yRef, yMeas;
    
    assign yRef = {{32{1'b0}}, aR} * {{32{1'b0}}, bR};
    
    unsigned_mult #(
        .A_WIDTH(32),
        .B_WIDTH(32))
    u_mult (
        .clkIn(clk),
        .rstIn(rst),
        .aIn  (aR),
        .bIn  (bR),
        .yOut (yMeas));
    
endmodule