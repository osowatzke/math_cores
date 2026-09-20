`timescale 1 ns/1 ns

module unsigned_mult #(
    parameter   A_WIDTH    = 26,
    parameter   B_WIDTH    = 17,
    localparam  PROD_WIDTH = A_WIDTH + B_WIDTH) (
    input  wire clkIn,
    input  wire rstIn,
    input  wire [A_WIDTH - 1:0] aIn,
    input  wire [B_WIDTH - 1:0] bIn,
    output wire [PROD_WIDTH - 1:0] yOut);
    
    function integer get_num_slices(
        input integer A_WIDTH,
        input integer B_WIDTH);
        integer slices_per_stage;
        integer num_stages;
        begin
            slices_per_stage = (B_WIDTH + 16)/17;
            num_stages       = (A_WIDTH + 25)/26;
            get_num_slices   = num_stages * slices_per_stage;
        end
    endfunction
    
    localparam SLICES      = get_num_slices(A_WIDTH, B_WIDTH);
    localparam SWAP_SLICES = get_num_slices(B_WIDTH, A_WIDTH);
    localparam SWAP        = SLICES > SWAP_SLICES ? 1 : 0;
    
    localparam A_MOD_WIDTH = SWAP ? B_WIDTH : A_WIDTH;
    localparam B_MOD_WIDTH = SWAP ? A_WIDTH : B_WIDTH;
    
    wire [A_MOD_WIDTH - 1:0] a;
    wire [B_MOD_WIDTH - 1:0] b;
    
    assign a = SWAP ? bIn[A_MOD_WIDTH-1:0] : aIn[A_MOD_WIDTH-1:0];
    assign b = SWAP ? aIn[B_MOD_WIDTH-1:0] : bIn[B_MOD_WIDTH-1:0];
    
    localparam SLICES_PER_STAGE = (B_MOD_WIDTH + 16)/17;
    localparam NUM_STAGES       = (A_MOD_WIDTH + 25)/26;
    localparam STAGE_DELAY      = SLICES_PER_STAGE + 1;
    
    genvar i, j;
    
    localparam STAGE_PROD_WIDTH = SLICES_PER_STAGE * 17 + 26;
    
    localparam Y_PAD_WIDTH = SLICES_PER_STAGE * 17 + NUM_STAGES * 26;
    wire [Y_PAD_WIDTH-1:0] yPad;
    
    wire [STAGE_PROD_WIDTH - 1:0] pStage [0:NUM_STAGES-1];
    
    wire [B_MOD_WIDTH - 1:0] bPipe [0:NUM_STAGES-1];
    
    generate
        for (i = 0; i < NUM_STAGES; i = i + 1)
        begin
            wire [25:0] aSlice;
            
            localparam A_START_IDX = 26*i;
            localparam A_END_IDX   = A_START_IDX + 25;
            
            if (A_END_IDX <= A_MOD_WIDTH) begin
                assign aSlice = a[A_END_IDX:A_START_IDX];
            end else begin
                localparam A_PAD = A_END_IDX - (A_MOD_WIDTH - 1);
                assign aSlice = {{A_PAD{1'b0}}, a[A_MOD_WIDTH-1:A_START_IDX]};
            end
            
            if (i == 0) begin
                assign bPipe[i] = b;
            end else begin
                pipe #(.DELAY(STAGE_DELAY), .WIDTH(B_MOD_WIDTH)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(bPipe[i-1]), .xOut(bPipe[i]));
            end            
            
            localparam USE_CIN = (i == 0) ? 0 : 1;
            
            wire [47:0] pC [0:SLICES_PER_STAGE-1];
            
            wire [25:0] aPipe [0:SLICES_PER_STAGE-1];
            
            for (j = 0; j < SLICES_PER_STAGE; j = j + 1)
            begin
                wire [16:0] bSlice;
            
                localparam B_START_IDX = 17*j;
                localparam B_END_IDX   = B_START_IDX + 16;
                
                if (B_END_IDX <= B_MOD_WIDTH)
                begin
                    assign bSlice = bPipe[i][B_END_IDX:B_START_IDX];
                end
                else
                begin
                    localparam B_PAD = B_END_IDX - (B_MOD_WIDTH - 1);
                    assign bSlice = {{B_PAD{1'b0}}, bPipe[i][B_MOD_WIDTH-1:B_START_IDX]};
                end

                wire [16:0] bSlicePipe;
		
                pipe #(.DELAY(j), .WIDTH(17)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(bSlice), .xOut(bSlicePipe));
            
                localparam USE_PCIN = (j == 0) ? 0 : 1;

                wire [47:0] pCSlice;
                
                if (j == 0)
                begin
                    assign pCSlice = {48{1'b0}};
                    localparam DELAY = i*STAGE_DELAY;
                    pipe #(.DELAY(DELAY), .WIDTH(26)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(aSlice), .xOut(aPipe[j]));
                end
                else
                begin
                    assign pCSlice = pC[j-1];
                    pipe #(.DELAY(1), .WIDTH(26)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(aPipe[j-1]), .xOut(aPipe[j]));
                end
                
                wire [47:0] cSlice;
                
                if (i == 0) begin
                    assign cSlice = {48{1'b0}};
                end else begin
                    localparam P_START_IDX = 26 + 17*j;
                    localparam P_END_IDX   = (j == SLICES_PER_STAGE - 1) ? STAGE_PROD_WIDTH - 1 : P_START_IDX + 16;
                    localparam C_PAD       = 48 - (P_END_IDX - P_START_IDX + 1);
                    
                    assign cSlice = {{C_PAD{1'b0}}, pStage[i-1][P_END_IDX:P_START_IDX]};
                end
                
                wire [47:0] cPipe;
                
                pipe #(.DELAY(j), .WIDTH(48)) pipe_c(.clkIn(clkIn), .rstIn(rstIn), .xIn(cSlice), .xOut(cPipe));
                
                wire [47:0] pSlice;
                
                mult_26x17 #(
                    .USE_CIN (USE_CIN),
                    .USE_PCIN(USE_PCIN))
                mult_i (
                    .clkIn(clkIn),
                    .rstIn(rstIn),
                    .aIn  (aPipe[j]),
                    .bIn  (bSlicePipe),
                    .cIn  (cPipe),
                    .pCIn (pCSlice),
                    .pOut (pSlice),
                    .pCOut(pC[j]));
                    
                localparam P_START_IDX = 17*j;
                if (j == (SLICES_PER_STAGE - 1)) begin
                    localparam P_WIDTH = STAGE_PROD_WIDTH - P_START_IDX;
                    localparam P_END_IDX = P_START_IDX + P_WIDTH - 1;
                    assign pStage[i][P_END_IDX:P_START_IDX] = pSlice[P_WIDTH-1:0];
                end else begin
                    localparam P_END_IDX = P_START_IDX + 16;
                    localparam DELAY = SLICES_PER_STAGE - 1 - j;
                    pipe #(.DELAY(DELAY), .WIDTH(17)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(pSlice[16:0]), .xOut(pStage[i][P_END_IDX:P_START_IDX]));
                end
            end
            localparam Y_START_IDX = i*26;
            if (i == (NUM_STAGES - 1)) begin
                localparam Y_END_IDX = Y_START_IDX + STAGE_PROD_WIDTH - 1;
                assign yPad[Y_END_IDX:Y_START_IDX] = pStage[i];
            end else begin
                localparam Y_END_IDX = Y_START_IDX + 25;
                localparam DELAY = 3*(NUM_STAGES-1-i);
                pipe #(.DELAY(DELAY), .WIDTH(26)) pipe_i(.clkIn(clkIn), .rstIn(rstIn), .xIn(pStage[i][25:0]), .xOut(yPad[Y_END_IDX:Y_START_IDX]));
            end
        end
    endgenerate
    
    assign yOut = yPad[PROD_WIDTH-1:0];
    
endmodule