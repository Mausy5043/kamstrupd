#!/bin/bash

# query hourly totals for a period of two days (48 hours)

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$((LOCALSECONDS - UTCSECONDS))

# create a place to store the data
datastore="/tmp/kamstrupd/data"
if [ ! -d "${datastore}" ]; then
  mkdir -p "${datastore}"
fi

datafile=$(mktemp "${datastore}/dataXXXXXX.csv")
