#!/usr/bin/env bash

DBFILE_1="electriciteit.sqlite3"
#DBFILE_2="electriciteit.sqlite3"

install_database_files() {
    echo "Installs are disabled for this version."
    exit 1
    mkdir -p "${HOME}/.sqlite3"
    recover_database_file ${DBFILE_1}
    if [ ! -e "${HOME}/.sqlite3/${DBFILE_1}" ]; then
        create_database_file "idf1"
    fi
}

backup_database_file() {
    echo "Backups are disabled for this version."
    exit 1
    if [ -e "${HOME}/.sqlite3/${1}" ]; then
        echo "Standby while making a backup of ${1} ..."
        sqlite3 "${HOME}/.sqlite3/${1}" ".backup /mnt/data/${1}"
    fi
}

recover_database_file() {
    echo "Recovery is disabled for this version."
    exit 1
    if [ -e "/mnt/data/${1}" ]; then
        echo "Standby while recovering ${1} from backup ..."
        cp "/mnt/data/${1}" "${HOME}/.sqlite3/"
    fi
}

create_database_file() {
    # WARNING!!
    # Calling this function from the wild will overwrite an existing database!
    #
    if [[ "${1}" == "idf1" ]]; then
        sqlite3 "${HOME}/.sqlite3/${DBFILE_1}" <bin/table31.sqlite3.sql
        sqlite3 "${HOME}/.sqlite3/${DBFILE_1}" 'PRAGMA journal_mode=WAL;'
    else
        echo "Unsupported functionality. Use the 'install_database_file' function instead!"
        exit 1
    fi
}

# check commandline parameters
for i in "$@"; do
    case $i in
    -i | --install)
        install_database_files
        ;;
    -b | --backup)
        backup_database_file ${DBFILE_1}
        ;;
    -r | --recover)
        recover_database_file ${DBFILE_1}
        ;;
    *)
        # unknown option
        echo "** Unknown option **"
        echo
        echo "Syntax:"
        echo "bakrecdb.sh [-i|--install] [-b|--backup] [-r|--recover]"
        echo
        exit 1
        ;;
    esac
done
