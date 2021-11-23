#!/bin/bash

install_package() {
    # See if packages are installed and install them.
    package=$1
    echo "*********************************************************"
    echo "* Requesting ${package}"
    status=$(dpkg-query -W -f='${Status} ${Version}\n' "${package}" 2>/dev/null | wc -l)
    if [ "${status}" -eq 0 ]; then
        echo "* Installing ${package}"
        echo "*********************************************************"
        sudo apt-get -yuV install "${package}"
    else
        echo "* Already installed !!!"
        echo "*********************************************************"
    fi
    echo
}

getfilefromserver() {
    file="${1}"
    mode="${2}"

    #if [ ! -f "${HOME}/${file}" ]; then
    cp -rvf "/srv/config/${file}" "${HOME}/.config/"
    chmod -R "${mode}" "${HOME}/.config/${file}"
    #fi
}

# ME=$(whoami)
HERE=$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)
# MINIT=$(echo $RANDOM/555 | bc)

required_commonlibversion="1.0.0"
commonlibbranch="v1_0"

pushd "${HERE}" || exit 1
    # shellcheck disable=SC1091
    source ./bin/constants.sh
popd || exit 1

echo
# shellcheck disable=SC2154
echo -n "Started installing ${app_name} on "; date
echo
# echo "MINIT = ${minit}"

sudo apt-get update
# LFTP package is needed for accessing the remote website.
install_package "lftp"
# Python3 package and associates
install_package "python3"
install_package "build-essential"
install_package "python3-dev"
install_package "python3-pip"
# Support for matplotlib & numpy needs to be installed seperately
install_package "libatlas-base-dev"
install_package "libxcb1"
# install_package "libpng16-16"
# install_package "libjpeg62"
install_package "libopenjp2-7"
install_package "libtiff5"

# Support for serial port
install_package "picocom"
install_package "python3-serial"

# SQLite3 support (incl python3)
install_package "sqlite3"

echo
echo "*********************************************************"
echo
python3 -m pip install --upgrade pip setuptools wheel
pushd "${HERE}" || exit 1
  python3 -m pip install -r requirements.txt
popd || exit 1

# install account key from local fileserver
getfilefromserver "solaredge" "0740"
getfilefromserver "zappi" "0740"
cp -rvf "/srv/config/.lftprc" "${HOME}/"
chmod -R 0740 "${HOME}/.lftprc"

commonlibversion=$(python3 -m pip freeze | grep mausy5043 | cut -c 26-)
if [ "${commonlibversion}" != "${required_commonlibversion}" ]; then
  echo
  echo "*********************************************************"
    echo "Install common python functions..."
    python3 -m pip uninstall -y mausy5043-common-python
    python3 -m pip install "git+https://gitlab.com/mausy5043-installer/mausy5043-common-python.git@${commonlibbranch}#egg=mausy5043-common-python"
    echo
    echo -n "Installed: "
    python3 -m pip list | grep mausy5043
  echo
fi

pushd "${HERE}" || exit 1
    # To suppress git detecting changes by chmod:
    git config core.fileMode false
    # set the branch
    if [ ! -e "${HOME}/.${app_name}.branch" ]; then
        echo "zappi" >"${HOME}/.${app_name}.branch"
    fi
    chmod -x ./services/*

    # install services and timers
    sudo cp ./services/*.service /etc/systemd/system/
    sudo cp ./services/*.timer /etc/systemd/system/
    #
    sudo systemctl daemon-reload
    #
    sudo systemctl enable kamstrup.trend.day.timer &
    sudo systemctl enable kamstrup.trend.month.timer &
    sudo systemctl enable kamstrup.trend.year.timer &
    sudo systemctl enable kamstrup.update.timer &

    sudo systemctl enable kamstrup.kamstrup.service &
    sudo systemctl enable kamstrup.solaredge.service &
    sudo systemctl enable kamstrup.fles.service &
    #
    wait
    sudo systemctl start kamstrup.trend.day.timer
    sudo systemctl start kamstrup.trend.month.timer
    sudo systemctl start kamstrup.trend.year.timer
    sudo systemctl start kamstrup.update.timer    # this will also start the daemon!

    echo "Starting services..."
    sudo systemctl start kamstrup.kamstrup.service &
    sudo systemctl start kamstrup.solaredge.service &
    sudo systemctl start kamstrup.fles.service &
    wait

popd || exit 1

echo
echo "*********************************************************"
echo -n "Finished installation of ${app_name} on "; date
echo
