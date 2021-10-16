(below info translated from Dutch was correct in 2016; checked in 2021)
## P1 Converter Cable, Versie 2

The P1 Converter Cable enables reading the P1-port (RJ11) of a Dutch Smart meter conform NEN-NTA8130 (DSMR 3 or 4).
As soon as the cable is connected between the meter and a computer the P1 telegrams will be offered via the COM-port
that is emulated by the hardwareport that the USB plug is connected to.

 - Cable (example; there are many suppliers): https://www.okaphone.com/artikel.asp?id=484214
 - Drivers (not tested): http://www.ftdichip.com/Drivers/VCP.htm

Refer to [www.smartmeterdashboard.nl](https://sites.google.com/site/nta8130p1smartmeter/downloads) for additional info/documentation.

To write your own datalogger the following COM-port settings may be used:
In case of a DSMR2/3 meter:
 - 9600 Baud
 - EVEN Parity
 - 7 Databits
 - 1 Stopbit
 - XON/XOFF
 - NO RTS/CTS

In case of a DSMR4 meter:
 - 115200 Baud
 - NO Parity
 - 8 Databits
 - 1 Stopbit
 - XON/XOFF
 - NO RTS/CTS
