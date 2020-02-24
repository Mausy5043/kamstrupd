#!/bin/bash

# query daily totals for a period of one month

pushd "${HOME}/kamstrupd" >/dev/null || exit 1

./scripts/kam43.py -m
./scripts/upload.sh --upload

popd >/dev/null || exit
