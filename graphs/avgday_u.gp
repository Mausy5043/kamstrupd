#!/usr/bin/env gnuplot

# graph of current power usage


set output "/tmp/kamstrupd/site/img/kam_avg_day_u.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 640,640
set datafile separator ';'
set datafile missing "NaN"    # Ignore missing values
set grid front
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
set title "Gemiddeld uurverbruik ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** X-axis *****
set xlabel "uur"
set xtics rotate by -60

# ***************************************************************** Y-axis *****
set ylabel "Verbruik [Wh]"

# ***************************************************************** Legend *****
set key inside top left horizontal box
set key samplen 1
set key reverse Left

# ***************************************************************** Output *****
set style data boxplot
set style boxplot outliers pointtype 7
set style fill solid 0.5 border -1
set boxwidth 0.75
set pointsize 0.5

# ****************************************************************** PLOT ******
plot kamdata using (1):1 title columnheader(1), \
     for [i=2:23] '' using (i):i title columnheader(i)

