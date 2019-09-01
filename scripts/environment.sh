#!/bin/bash

# query hourly totals for a period of two days (48 hours)

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
# shellcheck disable=SC2034
UTCOFFSET=$((LOCALSECONDS - UTCSECONDS))

# create a place to store the data
datastore="/tmp/kamstrupd"
if [ ! -d "${datastore}" ]; then
  mkdir -p "${datastore}"
fi

# create a place to store the website files for uploading
site="/tmp/kamstrupd/site"
if [ ! -d "${site}/img" ]; then
  mkdir -p "${site}/img"
fi

# shellcheck disable=SC2034
kamdata=$(mktemp "${datastore}/dataXXXXXX.csv")
