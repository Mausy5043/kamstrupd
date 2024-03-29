#!/bin/bash

# query daily totals for a period of one month

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

pushd "${HERE}" >/dev/null || exit 1
    # shellcheck disable=SC1091
    source ./constants.sh

    CURRENT_EPOCH=$(date +'%s')
    # do some maintenance
    # shellcheck disable=SC2154
    echo "${db_full_path} re-indexing... "
    sqlite3 "${db_full_path}" "REINDEX;"

    echo -n "${db_full_path} integrity check:   "
    chk_result=$(sqlite3 "${db_full_path}" "PRAGMA integrity_check;")
    echo " ${chk_result}"
    if [ "${chk_result}" == "ok" ]; then
        echo "${db_full_path} copying... "
        # shellcheck disable=SC2154
        cp "${db_full_path}" "${database_path}/backup/"

        # Keep upto 10 years of data
        echo "${db_full_path} vacuuming... "
        PURGE_EPOCH=$(echo "${CURRENT_EPOCH} - (3660 * 24 * 3600)" |bc)
        sqlite3 "${db_full_path}" \
                "DELETE FROM kamstrup WHERE sample_epoch < ${PURGE_EPOCH};"
        sqlite3 "${db_full_path}" \
                "DELETE FROM production WHERE sample_epoch < ${PURGE_EPOCH};"
        sqlite3 "${db_full_path}" \
                "DELETE FROM zappi WHERE sample_epoch < ${PURGE_EPOCH};"
    fi

    ./trend.py --days 0

popd >/dev/null || exit
