#!/bin/sh

echo "--Looking for entries with zero value counter--"
mysql -h sql -e "USE domotica; SELECT * FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
echo
