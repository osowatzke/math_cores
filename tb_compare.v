`timescale 1 ns/1 ns

module tb_compare #(
    parameter WIDTH = 32) (
    input  wire clkIn,
    input  wire rstIn,
    input  wire validIn,
    input  wire [WIDTH - 1:0] refIn,
    input  wire [WIDTH - 1:0] measIn,
    output wire errOut);
    
    reg errR;
    
    always @(posedge clkIn) begin
        if (rstIn == 1) begin
            errR <= 0;
        end else begin
            if ((validIn == 1) && (refIn !== measIn)) begin
                $display("Mismatch at time %t. Meas (0x%016X) != Ref (0x%016X)", $realtime, measIn, refIn);
                errR <= 1;
            end
        end
    end
    
    assign errOut = errR;

endmodule
    