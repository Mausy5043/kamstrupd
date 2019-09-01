#!/usr/bin/env gnuplot

# graph of current power usage

# datafiles
print kamdata
set output "/tmp/kamstrupd/kam_pastday.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 1280,320
set datafile separator ','
set datafile missing "NaN"    # Ignore missing values
set grid front
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
if (GPVAL_VERSION == 4.6) {epoch_compensate = 946684800} else {if (GPVAL_VERSION == 5.0) {epoch_compensate = 0}}
# Positions of split between graphs
LMARG = 0.06
LMPOS = 0.40
MRPOS = 0.73
RMARG = 0.94

min(x,y) = (x < y) ? x : y
max(x,y) = (x > y) ? x : y

# ********************************************************* Statistics     *****
# stats to be calculated here of column 1 (hour)
stats kamdata using 1 name "X" nooutput

Xh_min = X_min
Xh_max = X_max



set title "Verbruik recent ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                            PLOT: past hours
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# ***************************************************************** X-axis *****
set xlabel "uur"             # X-axis label
#set xdata time               # Data on X-axis should be interpreted as time
#set timefmt "%s"             # Time in log-file is given in Unix format
#set format x "%a %d"            # Display time in 24 hour notation on the X axis
#set xrange [ Xh_min : Xh_max ]

# ***************************************************************** Y-axis *****
set ylabel "Verbruik [Wh]"
#set yrange [ 0 : Ymax ]

# ***************************************************************** Legend *****
set key inside top left horizontal box
set key samplen 1
set key reverse Left

# ***************************************************************** Output *****
# set arrow from graph 0,graph 0 to graph 0,graph 1 nohead lc rgb "red" front
# set arrow from graph 1,graph 0 to graph 1,graph 1 nohead lc rgb "green" front
#set object 1 rect from screen 0,0 to screen 1,1 behind
#set object 1 rect fc rgb "#eeeeee" fillstyle solid 1.0 noborder
#set object 2 rect from graph 0,0 to graph 1,1 behind
#set object 2 rect fc rgb "#ffffff" fillstyle solid 1.0 noborder

#set lmargin at screen LMARG
#set rmargin at screen LMPOS

# ***** PLOT *****
plot datafile using 1:2
#plot ifnamew \
#      using ($1+utc_offset):4 title " Vermogen [W]" with lines lw 0.1 lc rgb "#ccbb0000"
#      # with points pt 5 ps 0.2 fc rgb "#ccbb0000" \
