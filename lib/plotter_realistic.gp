#### Basic gnuplot related settings ####
# input_file is a gnuplot command line argument set by 
# $ gnuplot -e "input_file='Data.dat';pps_unit='K';bps_unit='G';tr1='tr2i';tr2='tr2i';" Data.gp 
INPUT_DATA=input_file
OUTPUT_BASENAME=INPUT_DATA[:strlen(INPUT_DATA)-5]."_"
TR1=tr1
TR2=tr2

PPS_UNIT=pps_unit
#THIS GNUPLOT FILE IS ONLY FOR PPS, THUS WE ONLY SET THIS VAR, 
#BUT OMIT IT DURING PROCESSING
BPS_UNIT=bps_unit


#set term postscript

#this makes legend out of the diagram and gets these titles from the first line
#of the datafile
#set key autotitle columnhead out

#setting output style
set term post color eps 20
#set size 0.7,0.7

#set separator
set datafile separator ","

#Setting the x and y axis's fonts
#set xtics font "Times-Roman, 28" 
#set ytics font "Times-Roman, 28"

#Setting x and y axis's labels and their offset
set ylabel PPS_UNIT."Packet/s" offset 1.5,0 font "Times-Roman, 28"
#set xlabel "Packet size" offset 0,0.5 font "Times-Roman, 28"


#Setting the legend to bottom-right with 5 length of the sample, with 4 vertical spacing and with 18 font-size
set key right top samplen 5 spacing 4 



# We need to set lw in order for error bars to actually appear.
set style histogram errorbars linewidth 1

# Make the bars semi-transparent so that the errorbars are easier to see.
set style fill solid 0.3
set bars front

#PACKET/S
set output OUTPUT_BASENAME."_".PPS_UNIT."pps.eps"
plot INPUT_DATA every ::1::3 using 3:2:4:xticlabels(1) w hist ti TR1


#BIT/S
#Setting x and y axis's labels and their offset
set ylabel BPS_UNIT."bit/s" offset 1.5,0 font "Times-Roman, 28"
set output OUTPUT_BASENAME."_".BPS_UNIT."bps.eps"
plot INPUT_DATA every ::4::6 using 3:2:4:xticlabels(1) w hist ti TR1
