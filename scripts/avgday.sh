#!/bin/bash

# query hourly totals for a period of two days

pushd "${HOME}/kamstrupd" >/dev/null || exit 1

./scripts/kam45.py -a
./scripts/upload.sh --upload

popd >/dev/null || exit
