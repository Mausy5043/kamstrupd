# KAMSTRUPd

Read data from a KAMSTRUP smart meter.  
Store the data in a SQLite3 database.  
Regularly create trendgraphs.  
Upload trendgraphs to an external website for perusal.

## Installing

```
sudo su -
cd /home/pi
git clone https://gitlab.com/mausy5043-diagnostics/kamstrupd.git
cd kamstrupd
./install.sh
./update.sh
```

## Requirements
### Hardware:
The Python scripts have been shown to work correctly on the following hardware:
 - Raspberry Pi 3B+
