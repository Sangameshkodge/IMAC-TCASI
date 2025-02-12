

//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    13:56:58 07/10/2019 
// Design Name: 
// Module Name:    Accumulator
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module register(
    	output wire [5:0] Q,
	input [5:0]D,
	input clk,
	input reset,
	input en
    );

reg [5:0] outreg;
assign Q = outreg;

initial 
		begin 
			outreg<=5'b0;
		end



	always @(posedge clk or posedge reset )
		begin

			if (reset == 1'b1)
				outreg<=0;
			else
				if (en == 1'b1)
					outreg <= D;
				else 
					outreg <= D;		
		end
endmodule
