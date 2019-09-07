#!/usr/bin/env gnuplot

# graph of current power usage and production


set output "/tmp/kamstrupd/site/img/kam_vs_month_p.png"

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
#                                                             PLOT: Production
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
set title "Maandproductie afgelopen jaren ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** X-axis *****
set xlabel "jaar-maand"
set xtics rotate by -60

# ***************************************************************** Y-axis *****
set ylabel "Productie [Wh]"

# ***************************************************************** Legend *****
set key off

# ***************************************************************** Output *****
set style data histograms
set style histogram rowstacked
set style fill solid noborder
set boxwidth 0.75

# ****************************************************************** PLOT ******
plot kamdata using 3:xtic(1) lc "magenta"
