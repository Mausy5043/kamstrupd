#!/usr/bin/env gnuplot

# graph of current power usage


set output "/tmp/kamstrupd/site/img/kam_avg_day_p.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 1280,640
set datafile separator ';'
set datafile missing "NaN"    # Ignore missing values
set grid front noxtics ytics
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
if (GPVAL_VERSION == 4.6) {epoch_compensate = 946684800} else {if (GPVAL_VERSION == 5.0) {epoch_compensate = 0}}

# ********************************************************* Functions      *****
min(x,y) = (x < y) ? x : y
max(x,y) = (x > y) ? x : y


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                             PLOT: Usage
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
set title "Gemiddelde uuropbrengst ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** X-axis *****
set xlabel "uur"
set xtics rotate by -60
set xrange [0:25]
set xtics ("00h" 1, "06h" 7, "12h" 13, "18h" 19, "23h" 24)

# ***************************************************************** Y-axis *****
set ylabel "Productie [Wh]"
set yrange [:2000]

# ***************************************************************** Legend *****
set key off

# ***************************************************************** Output *****
set style data boxplot
set style boxplot nooutliers # pointtype 7
set style fill solid 0.5 border -1
set boxwidth 0.75
set pointsize 0.5

# ****************************************************************** PLOT ******
plot for [i=1:24] kamdata using (i):i lc rgb 'blue'
