#!/usr/bin/env gnuplot

# graph of current power usage


set output "/tmp/kamstrupd/site/img/kam_vs_month_u.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 1280,320
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
set title "Maandverbruik afgelopen jaren ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** X-axis *****
set xlabel "maand"
set xtics rotate by -60

# ***************************************************************** Y-axis *****
set ylabel "Verbruik [kWh]"

# ***************************************************************** Legend *****
set key inside top left horizontal box
set key samplen 1
set key reverse Left

# ***************************************************************** Output *****
set style data histograms
set style histogram clustered gap 1.0
set style fill solid noborder
set boxwidth 0.75

# ****************************************************************** PLOT ******
plot kamdata using 2:xtic(1) title columnheader(2), \
     for [i=3:7] '' using i title columnheader(i)

