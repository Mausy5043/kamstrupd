#!/usr/bin/env bash

DBFILE="electriciteit.sqlite3"

install_database_file() {
    mkdir -p "${HOME}/.sqlite3"
    recover_database_file
    if [ ! -e "${HOME}/.sqlite3/${DBFILE}" ]; then
        create_database_file "idf"
    fi
}

backup_database_file() {
    if [ -e "${HOME}/.sqlite3/${DBFILE}" ]; then
        sqlite3 .backup "${HOME}/.sqlite3/${DBFILE}" "/mnt/data/${DBFILE}"
    fi
}

recover_database_file() {
    if [ -e "/mnt/data/${DBFILE}" ]; then
        cp "/mnt/data/${DBFILE}" "${HOME}/.sqlite3/"
    fi
}

create_database_file() {
    # WARNING!!
    # Calling this function from the wild will overwrite an existing database!
    #
    if [[ "${1}" == "idf" ]]; then
        sqlite3 "${HOME}/.sqlite3/${DBFILE}" < table31.sqlite3.sql
    else
        echo "Unsupported functionality. Use the 'install_database_file' function instead!"
        exit 1
    fi
}

# check commandline parameters
for i in "$@"
do
  case $i in
    -i|--install)
        install_database_file
        ;;
    -b|--backup)
        backup_database_file
        ;;
    -r|--recover)
        recover_database_file
        ;;
    *)
        # unknown option
        echo "** Unknown option **"
        echo
        echo "Syntax:"
        echo "kamfile.sh [-i|--install] [-b|--backup] [-r|--recover]"
        echo
        exit 1
        ;;
  esac
done
