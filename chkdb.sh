#!/bin/bash

arg1="$1"


HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)
pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./bin/constants.sh
popd || exit 1


echo "--Checking integrity--"
sqlite3 "${db_full_path}" "PRAGMA integrity_check;"
echo

echo "--Looking for entries with zero value counter--"
sqlite3 "${db_full_path}" "SELECT * FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
echo

if [[ "$arg1" = "-d" ]]; then
  echo "Deleting data in 5s.."
  sleep 5 && sqlite3 "${db_full_path}" "DELETE FROM kamstrup WHERE (T1in = 0 OR T2in = 0);"
else
  echo "To remove zero value entries from the database, use:"
  echo "chkdb.sh -d"
  echo
fi
