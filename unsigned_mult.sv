module unsigned_mult #(
    parameter   A_WIDTH    = 26,
    parameter   B_WIDTH    = 17,
    localparam  PROD_WIDTH = A_WIDTH + B_WIDTH) (
    input  wire clkIn,
    input  wire rstIn,
    input  wire [A_WIDTH - 1:0] aIn,
    input  wire [B_WIDTH - 1:0] bIn,
    input  wire [PROD_WIDTH - 1:0] yOut);
    
    function integer get_num_slices;
        input integer A_WIDTH;
        input integer B_WIDTH;
        reg slices_per_stage;
        reg num_stages;
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
    
    assign a = SWAP ? b[A_MOD_WIDTH-1:0] : a[A_MOD_WIDTH-1:0];
    assign b = SWAP ? a[B_MOD_WIDTH-1:0] : b[B_MOD_WIDTH-1:0];
    
    localparam SLICES_PER_STAGE = (B_MOD_WIDTH + 16)/17;
    localparam NUM_STAGES       = (A_MOD_WIDTH + 25)/26;
    
    genvar i, j;
    
    localparam STAGE_PROD_WIDTH = SLICES_PER_STAGE * 17 + 26;
    
    wire [STAGE_PROD_WIDTH - 1:0] pStage [0:NUM_STAGES-1];
    
    generate
        for (i = 0; i < NUM_STAGES; i = i + 1)
        begin
            wire [25:0] aSlice;
            
            localparam A_START_IDX = 26*i;
            localparam A_END_IDX   = A_START_IDX + 25;
            
            if (A_END_IDX <= A_MOD_WIDTH)
            begin
                assign aSlice = a[A_END_IDX:A_START_IDX];
            end
            else
            begin
                localparam A_PAD = A_MOD_WIDTH - A_END_IDX - 1;
                assign aSlice = {{A_PAD{1'b0}}, a};
            end
            
            localparam USE_C = (i == 0) ? 0 : 1;
            
            wire [47:0] pC [0:SLICES_PER_STAGE-1];
            
            for (j = 0; j < SLICES_PER_STAGE; j = j + 1)
            begin
                wire [16:0] bSlice;
            
                localparam B_START_IDX = 17*i;
                localparam B_END_IDX   = B_START_IDX + 16;
                
                if (B_END_IDX <= B_MOD_WIDTH)
                begin
                    assign bSlice = b[A_END_IDX:A_START_IDX];
                end
                else
                begin
                    localparam B_PAD = B_MOD_WIDTH - B_END_IDX - 1;
                    assign bSlice = {{B_PAD{1'b0}}, b};
                end
            
                localparam USE_PCIN = (j == 0) ? 0 : 1;

                wire [47:0] pCSlice;
                
                if (j == 0)
                begin
                    assign pCSlice = {48{1'b0}};
                end
                else
                begin
                    assign pCSlice = pC[j-1];
                end
                
                wire [47:0] cSlice;
                
                if (i == 0)
                begin
                    assign cSlice = {48{1'b0}};
                end
                else
                begin
                    localparam P_START_IDX = 26 + 17*(j-1);
                    localparam P_END_IDX   = (j == SLICES_PER_STAGE - 1) ? P_START_IDX + 16 : STAGE_PROD_WIDTH - 1;
                    localparam C_PAD       = 48 - (P_END_IDX - P_START_IDX + 1);
                    
                    assign cSlice = {{C_PAD{1'b0}}, pStage[i-1][P_END_IDX:P_START_IDX]};
                end
                
                wire [47:0] pSlice;
                
                mult_26x17 #(
                    .USE_C   (USE_C),
                    .USE_PCIN(USE_PCIN))
                mult_i (
                    .clkIn(clkIn),
                    .rstIn(rstIn),
                    .aIn  (aSlice),
                    .bIn  (bSlice),
                    .cIn  (cSlice),
                    .pCIn (pCSLice),
                    .pOut (pSlice),
                    .pCOut(pC[j]));
                    
                localparam P_START_IDX = 17*j;
                if (j == (SLICES_PER_STAGE - 1)) begin
                    localparam P_END_IDX = P_START_IDX + 47;
                    assign pStage[i][P_END_IDX:P_START_IDX] = pSlice;
                end else begin
                    localparam P_END_IDX = P_START_IDX + 16;
                    assign pStage[i][P_END_IDX:P_START_IDX] = pSlice[16:0];
                end
            end
            localparam Y_START_IDX = i*26;
            if (i == (NUM_STAGES - 1)) begin
                localparam Y_END_IDX = Y_START_IDX + STAGE_PROD_WIDTH - 1;
                assign yOut[Y_END_IDX:Y_START_IDX] = pStage[i];
            end else begin
                localparam Y_END_IDX = Y_START_IDX + 25;
                assign yOut[Y_END_IDX:Y_START_IDX] = pStage[i][25:0];
            end
        end
    endgenerate
    
endmodule