#!/bin/bash

# query monthly totals for a period of n years

pushd "${HOME}/kamstrupd" >/dev/null || exit 1

./scripts/kam43.py -y1
./scripts/kam43.py -y2
./scripts/kam44.py -m
./scripts/avgday.sh

./scripts/upload.sh --upload

popd >/dev/null || exit
