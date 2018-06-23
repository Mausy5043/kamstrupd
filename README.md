# KAMSTRUPd [![pipeline status](https://gitlab.com/mausy5043-diagnostics/kamstrupd/badges/v3/pipeline.svg)](https://gitlab.com/mausy5043-diagnostics/kamstrupd/commits/v3)

## Installing

```
sudo su -
cd /path/to/where/you/want/store/kamstrupd
git clone https://gitlab.com/mausy5043-diagnostics/kamstrupd.git
cd kamstrupd
./install.sh
./update.sh
```

## Requirements
### Hardware:
The python scripts have been shown to work correctly on the following hardware:
 - Raspberry Pi 1B

## Attribution
The python code for the daemons is based on previous work by
- [Charles Menguy](http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
- [Sander Marechal](http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)
