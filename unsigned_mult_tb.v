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
    reg validR;
    
    always @(posedge clk) begin
        if (rst == 1) begin
            aR  <= 0;
            bR  <= 0;
            validR <= 0;
        end else begin
            aR  <= $random;
            bR  <= $random;
            validR <= 1;
        end
    end
    
    wire [63:0] y, yRef, yMeas;
    wire validPipe;
    
    assign y = {{32{1'b0}}, aR} * {{32{1'b0}}, bR};
    
    pipe #(.DELAY(7), .WIDTH(64)) pipe_y    (.clkIn(clk), .rstIn(rst), .xIn(y),      .xOut(yRef));
    pipe #(.DELAY(7), .WIDTH(1))  pipe_valid(.clkIn(clk), .rstIn(rst), .xIn(validR), .xOut(validPipe));
    
    unsigned_mult #(
        .A_WIDTH(32),
        .B_WIDTH(32))
    u_mult (
        .clkIn(clk),
        .rstIn(rst),
        .aIn  (aR),
        .bIn  (bR),
        .yOut (yMeas));
        
    wire err;
    
    tb_compare #(
        .WIDTH(64))
    comp_i (
        .clkIn(clk),
        .rstIn(rst),
        .validIn(validPipe),
        .refIn(yRef),
        .measIn(yMeas),
        .errOut(err));
    
    initial begin
        $timeformat(-9, 3, " ns", 10);
        #10000
        if (err) begin
            $display("One or More Tests Failed :(");
        end else begin
            $display("All Tests Passed :)");
        end
        $finish();
    end 
    
endmodule