
//`timescale 1ns / 1ps
module testbench();

wire [13:0] out;
reg [4:0] in;
reg clk ;
reg en ; 
reg reset;

initial 
begin 
		reset <= 1'b1;
		clk <= 1'b1;
		en <= 1'b0;
	#8	reset<=1'b0;
	#8	en <= 1'b1;		
	#0	in<=5'b01010;
	#8	in<=5'b01011;
	#8	in<=5'b01100;
	#8	in<=5'b01101;
	#8	in<=5'b01110;
	#8	in<=5'b01111;
	#8	en <= 1'b0;
end

accumulator DUT(.out(out), .in (in), .clk(clk), .en(en), .reset(reset));

always
begin
	#4	 clk=~clk;
end

endmodule
