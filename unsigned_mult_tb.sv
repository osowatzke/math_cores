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
    
    parameter A_WIDTH = 64;
    parameter B_WIDTH = 64;
    parameter PROD_WIDTH = A_WIDTH + B_WIDTH;
    
    reg [A_WIDTH-1:0] aR;
    reg [B_WIDTH-1:0] bR;
    reg validR;
    
    class random #(parameter WIDTH = 32);
        localparam NUM_WORDS = (WIDTH + 31)/32;
        localparam WIDTH_PAD = NUM_WORDS * 32;
        static function [WIDTH-1:0] randint();
            reg [31:0] randomWord;
            reg [WIDTH_PAD-1:0] randPad;
            integer i;
            begin
                randPad = 0;
                for (i = 0; i < NUM_WORDS; i = i + 1) begin
                    randomWord = $random;
                    randPad = randPad | ({{(WIDTH_PAD - WIDTH){1'b0}}, randomWord} << (32*i));
                end
                randint = randPad[WIDTH-1:0];
            end
        endfunction
    endclass
    
    function int latency(
        input int A_WIDTH,
        input int B_WIDTH);
        int slices, slicesSwap;
        int stages, stagesSwap;
        $display("A_WIDTH = %d", A_WIDTH);
        $display("B_WIDTH = %d", B_WIDTH);
        slices = (B_WIDTH + 16)/17;
        stages = (A_WIDTH + 25)/26;
        slicesSwap = (A_WIDTH + 16)/17;
        stagesSwap = (B_WIDTH + 25)/26;
        if ((slices * stages) > (slicesSwap * stagesSwap)) begin
            slices = slicesSwap;
            stages = stagesSwap;
        end
        $display("slices = %d", slices);
        $display("stages = %d", stages);
        latency = (2 + slices)*stages - (stages - 1);
    endfunction;
    
    always @(posedge clk) begin
        if (rst == 1) begin
            aR  <= 0;
            bR  <= 0;
            validR <= 0;
        end else begin
            aR  <= random#(A_WIDTH)::randint;
            bR  <= random#(B_WIDTH)::randint;
            validR <= 1;
        end
    end
    
    wire [PROD_WIDTH-1:0] y, yRef, yMeas;
    wire validPipe;
    
    parameter LATENCY = latency(A_WIDTH,B_WIDTH);
    
    assign y = {{(PROD_WIDTH-A_WIDTH){1'b0}}, aR} * {{(PROD_WIDTH-B_WIDTH){1'b0}}, bR};
    
    pipe #(.DELAY(LATENCY), .WIDTH(PROD_WIDTH)) pipe_y    (.clkIn(clk), .rstIn(rst), .xIn(y),      .xOut(yRef));
    pipe #(.DELAY(LATENCY), .WIDTH(1))          pipe_valid(.clkIn(clk), .rstIn(rst), .xIn(validR), .xOut(validPipe));
    
    unsigned_mult #(
        .A_WIDTH(A_WIDTH),
        .B_WIDTH(B_WIDTH))
    u_mult (
        .clkIn(clk),
        .rstIn(rst),
        .aIn  (aR),
        .bIn  (bR),
        .yOut (yMeas));
        
    wire err;
    
    tb_compare #(
        .WIDTH(PROD_WIDTH))
    comp_i (
        .clkIn(clk),
        .rstIn(rst),
        .validIn(validPipe),
        .refIn(yRef),
        .measIn(yMeas),
        .errOut(err));
    
    initial begin
        $timeformat(-9, 3, " ns", 10);
        #1000
        if (err) begin
            $display("One or More Tests Failed :(");
        end else begin
            $display("All Tests Passed :)");
        end
        $finish();
    end 
    
endmodule