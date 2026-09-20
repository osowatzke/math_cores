module pipe #(
    parameter DELAY = 1,
    parameter WIDTH = 32) (
    input  wire clkIn,
    input  wire rstIn,
    input  wire enIn = 1'b1,
    input  wire [WIDTH-1:0] xIn,
    output wire [WIDTH-1:0] xOut);
    
    generate
        if (DELAY == 0) begin
            assign xOut = xIn;
        end else begin
            reg [WIDTH-1:0] xR [0:DELAY-1];
            integer i;
            
            always @(posedge clkIn) begin
                for (i = 0; i < DELAY; i = i + 1) begin
                    if (rstIn == 1) begin
                        xR[i] <= 0;
                    end else begin
                        if (i == 0) begin
                            xR[i] <= xIn;
                        end else begin
                            xR[i] <= xR[i-1];
                        end
                    end
                end
            end
            
            assign xOut = xR[DELAY-1];
        end            
    endgenerate
    
endmodule