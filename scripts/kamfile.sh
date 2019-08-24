#!/usr/bin/env bash

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

install_database_file() {
    mkdir -p "${HOME}/.sqlite3"
    if [ ! -e "${HOME}/.sqlite3/electriciteit.sqlite3" ]; then
      if [ -e "/mnt/data/electriciteit.sqlite3" ]; then
        mv /mnt/data/electriciteit.sqlite3 "${HOME}/.sqlite3/"
      fi
    else
      echo ""
    fi
}

backup_database_file() {
#...

}


recover_database_file() {
#...
}
