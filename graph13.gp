#!/usr/bin/env gnuplot

# graph of current power usage

# datafiles
ifnamel = "/tmp/kamstrupd/mysql/kamyr.csv"
ifnamem = "/tmp/kamstrupd/mysql/kammr.csv"
ifnamer = "/tmp/kamstrupd/mysql/kamwr.csv"
set output "/tmp/kamstrupd/site/img/kamstrup13.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 1280,320
set datafile separator ';'
set datafile missing "NaN"    # Ignore missing values
set grid front
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
if (GPVAL_VERSION == 4.6) {epoch_compensate = 946684800} else {if (GPVAL_VERSION == 5.0) {epoch_compensate = 0}}
# Positions of split between graphs
LMARG = 0.06
LMPOS = 0.425
MRPOS = 0.71
RMARG = 0.94

# ************************************************************* Functions ******
# determine delta data
delta(x) = ( xD = x - old_x, old_x = x, xD <= 0 ? 0.1 : xD)
# lg(x)    = ( xL = x, xL == NaN ? NaN : log(xL) )
old_x = NaN

min(x,y) = (x < y) ? x : y
max(x,y) = (x > y) ? x : y

# ********************************************************* Statistics (R) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnamer using 2 name "X" nooutput

Xr_min = X_min + utc_offset - epoch_compensate
Xr_max = X_max + utc_offset - epoch_compensate

# stats to be calculated here for Y-axes
#stats ifnamer using (delta($3)) name "Yr1" nooutput
#old_x = NaN
#stats ifnamer using (delta($4)) name "Yr2" nooutput
#old_x = NaN

# ********************************************************* Statistics (M) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnamem using 2 name "X" nooutput

Xm_min = X_min + utc_offset - epoch_compensate
Xm_max = X_max + utc_offset - epoch_compensate

# stats to be calculated here for Y-axes
#stats ifnamem using (delta($3)) name "Ym1" nooutput
#old_x = NaN
#stats ifnamem using (delta($4)) name "Ym2" nooutput
#old_x = NaN

# ********************************************************* Statistics (L) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnamel using 2 name "X" nooutput
Xl_min = X_min + utc_offset - epoch_compensate
Xl_max = X_max + utc_offset - epoch_compensate

# stats for Y-axis
#stats ifnamel using (delta($3)) name "Yl1" nooutput
#old_x = NaN
#stats ifnamel using (delta($4)) name "Yl2" nooutput
#old_x = NaN

Ymax = 10
Ymin = 0

set multiplot layout 1, 3 title "Historisch verbruik ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                       LEFT PLOT: past year
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# ***************************************************************** X-axis *****
set xlabel "past year"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%m-%y"            # Display time in 24 hour notation on the X axis
set xrange [ Xl_min : Xl_max ]

# ***************************************************************** Y-axis *****
set ylabel "Verbruik [kWh]"
set yrange [ Ymin : * ]

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

set lmargin at screen LMARG
set rmargin at screen LMPOS - 0.025

# ***** PLOT *****
set style data boxes
set style fill solid noborder

plot ifnamel \
      using ($2+utc_offset):(delta($3+$4)/1000)  title "T1"  fc "green"  \
  ,'' using ($2+utc_offset):(delta($4)/1000)     title "T2"  fc "yellow"

old_x = NaN


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                     MIDDLE PLOT:  past month
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# ***************************************************************** X-axis *****
set xlabel "past month"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "wk %W"            # Display time in 24 hour notation on the X axis
set xrange [ Xm_min : Xm_max ]

# ***************************************************************** Y-axis *****
set ylabel " "
#set ytics format " "
set yrange [ Ymin : * ]

# ***************************************************************** Legend *****
unset key

# ***************************************************************** Output *****
set lmargin at screen LMPOS + 0.001
set rmargin at screen MRPOS

# ***** PLOT *****
plot ifnamem \
      using ($2+utc_offset):(delta($3+$4)/1000)  title "T1"  fc "green"  \
  ,'' using ($2+utc_offset):(delta($4)/1000)     title "T2"  fc "yellow"

old_x = NaN

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                      RIGHT PLOT: past week
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# ***************************************************************** X-axis *****
set xlabel "past week"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%a"            # Display time in 24 hour notation on the X axis
set xrange [ Xr_min : Xr_max ]
set xtics textcolor rgb "red"

# ***************************************************************** Y-axis *****
set ylabel " "
#set ytics format " "
set yrange [ Ymin : * ]

# ***************************************************************** Legend *****
unset key

# ***************************************************************** Output *****
set lmargin at screen MRPOS + 0.021
set rmargin at screen RMARG

# ***** PLOT *****
plot ifnamer \
      using ($2+utc_offset):(delta($3+$4)/1000)  title "T1"  fc "green"  \
  ,'' using ($2+utc_offset):(delta($4)/1000)     title "T2"  fc "yellow"

old_x = NaN

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                                 FINALIZING
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

unset multiplot
