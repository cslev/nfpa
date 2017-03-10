#### Basic gnuplot related settings ####
# input_file is a gnuplot command line argument set by 
# $ gnuplot -e "input_file='Data.dat';pps_unit='K';bps_unit='G';tr1='tr2i';tr2='tr2i';" Data.gp 
INPUT_DATA=input_file
OUTPUT_BASENAME=INPUT_DATA[:strlen(INPUT_DATA)-5]."_"
PPS_UNIT=pps_unit
BPS_UNIT=bps_unit
TR1=tr1
TR2=tr2

set term postscript 
set termoption dashed

#this makes legend out of the diagram and gets these titles from the first line 
#of the datafile
#set key autotitle columnhead out   

#setting output style
set term post noenh color eps 20
#set size 0.7,0.7

#set separator
set datafile separator ","

#Setting the x and y axis's fonts
#set xtics font "Times-Roman, 28"
#set ytics font "Times-Roman, 28"

#Setting x and y axis's labels and their offset
set ylabel PPS_UNIT."Packet/s" offset 1.5,0 font "Times-Roman, 28"
set xlabel "Packet size" offset 0,0.5 font "Times-Roman, 28"


#Setting the legend to bottom-right with 5 length of the sample, with 4 vertical spacing and with 18 font-size
set key right top samplen 5 spacing 4 


#### Throughput packet/s ####
## SENT VS RECV ###
#Setting output
set output OUTPUT_BASENAME."sent_recv_".PPS_UNIT."pps.eps"

#this actually puts out the results
p INPUT_DATA u 1:2:2:2:xtic(1) with yerrorlines pt 4 ps 3 lw 10 lt 1  title "Theoretical", \
  INPUT_DATA u 1:4:3:5:xtic(1) with yerrorlines pt 8 ps 2 lw 6 lt 2  title "Sent-".TR1, \
  INPUT_DATA u 1:7:6:8:xtic(1) with yerrorlines pt 10 ps 2 lw 6 lt 3 title "Recv-".TR1, \
  INPUT_DATA u 1:22:21:23:xtic(1) with yerrorlines pt 25 ps 2 lw 6 lt 25 title "Sent-".TR2, \
  INPUT_DATA u 1:25:24:26:xtic(1) with yerrorlines pt 13 ps 2 lw 6 lt 4 title "Recv-".TR2
  


### MISSED PACKETS ###
#Setting output
set output OUTPUT_BASENAME."miss_".PPS_UNIT."pps.eps"
p INPUT_DATA u 1:10:9:11:xtic(1) with yerrorlines pt 9 ps 2 lw 6 lt 4 title "Miss-".TR1, \
  INPUT_DATA u 1:28:27:29:xtic(1) with yerrorlines pt 10 ps 2 lw 6 lt 3 title "Miss-".TR2
  

#### Throughput Mbit/s #####
## SENT VS RECV ###
#Setting output
set output OUTPUT_BASENAME."sent_recv_".BPS_UNIT."bps.eps"
set ylabel BPS_UNIT."bit/s" offset 1.5,0 font "Times-Roman, 28"

#this actually puts out the results
p INPUT_DATA u 1:13:12:14:xtic(1) with yerrorlines pt 8 ps 2 lw 6 lt 2 title "Sent-".TR1, \
  INPUT_DATA u 1:16:15:17:xtic(1) with yerrorlines pt 10 ps 2 lw 6 lt 3 title "Recv-".TR1, \
  INPUT_DATA u 1:31:30:32:xtic(1) with yerrorlines pt 25 ps 2 lw 6 lt 25 title "Sent-".TR2, \
  INPUT_DATA u 1:34:33:35:xtic(1) with yerrorlines pt 13 ps 2 lw 6 lt 4 title "Recv-".TR2


### DIFFERENCE BETWEEN SENT BPS AND RECV BPS
## SENT VS RECV ###
#Setting output
set output OUTPUT_BASENAME."diff_".BPS_UNIT."bps.eps"
p INPUT_DATA u 1:19:18:20:xtic(1) with yerrorlines pt 9 ps 2 lw 6 lt 4 title "Diff-".TR1, \
  INPUT_DATA u 1:37:36:38:xtic(1) with yerrorlines pt 10 ps 2 lw 6 lt 3 title "Diff-".TR2


