#!/usr/bin/env bash

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)

echo "Can't use upload in this version"
exit 1

copy_default_page() {
    pushd "${HERE}" >/dev/null || exit 1
    cp ../web/default.md /tmp/kamstrupd/site
    popd >/dev/null || exit
}

make_script() {
    {
        echo "# DO NOT EDIT"
        echo "# This file is created automatically."
        echo ""
        echo ""
        echo "set cmd:fail-exit yes;"
        echo "open hendrixnet.nl;"
        echo "cd 05.stream/;"
        echo "set cmd:fail-exit no;"
        echo "mirror --reverse --delete --verbose=3 -c /tmp/kamstrupd/site/ . ;"
    } >/tmp/kamstrupd/script.lftp
}

exec_script() {
    lftp -f /tmp/kamstrupd/script.lftp >/dev/null
}

# check commandline parameters
for i in "$@"; do
    case $i in
    -a | --all)
        copy_default_page
        make_script
        exec_script
        ;;
    -u | --upload)
        make_script
        exec_script
        ;;
    *)
        # unknown option
        echo "** Unknown option **"
        echo
        echo "Syntax:"
        echo "upload.sh [-a|--all] [-u|--upload]"
        echo
        exit 1
        ;;
    esac
done
