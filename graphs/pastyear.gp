#!/usr/bin/env gnuplot

# graph of this year's power usage and production


set output "/tmp/kamstrupd/site/img/kam_pastyear.png"

# ******************************************************* General settings *****
set terminal png enhanced font "Vera,9" size 1280,640
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
set multiplot layout 2,1


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                         TOP PLOT: Usage
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
set title "Verbruik per maand afgelopen jaren ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** X-axis *****
set xlabel "jaar-maand"
set xtics rotate by -60

# ***************************************************************** Y-axis *****
set ylabel "Verbruik [kWh]"

# ***************************************************************** Legend *****
set key inside top left horizontal box
set key samplen 1
set key reverse Left

# ***************************************************************** Output *****
set style data histograms
set style histogram rowstacked
set style fill solid noborder
set boxwidth 0.75

# ****************************************************************** PLOT ******
plot kamdata using 2:xtic(1) title "T1" lc "blue" \
        , '' using 3         title "T2" lc "orange"


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                         BTM PLOT: Production
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
set title "Levering per maand afgelopen jaren ".strftime("( %Y-%m-%dT%H:%M:%S )", time(0)+utc_offset)

# ***************************************************************** Y-axis *****
set ylabel "Levering [kWh]"

# ****************************************************************** PLOT ******
plot kamdata using 4:xtic(1) title "T1" lc "dark-green" \
        , '' using 5         title "T2" lc "green"
