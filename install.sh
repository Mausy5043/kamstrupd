#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

ME=$(whoami)
required_commonlibversion="0.6.0"
commonlibbranch="v0_6"

echo -n "Started installing KAMSTRUPd on "; date
minit=$(echo $RANDOM/555 |bc)
echo "MINIT = ${minit}"

install_package()
{
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
}

getfilefromserver() {
file="${1}"
mode="${2}"

#if [ ! -f "${HOME}/${file}" ]; then
  cp -rvf  "${HOME}/bin/.config/home/${file}" "${HOME}/"
  chmod    "${mode}" "${HOME}/${file}"
#fi
}

sudo apt-get update
# install_package "git"  # already installed by `mod-rasbian-netinst`
# LFTP package
install_package "lftp"

# Python 3 package and associates
install_package "python3"
install_package "build-essential"
install_package "python3-dev"
install_package "python3-pip"

# Support for serial port
install_package "picocom"
install_package "python3-serial"

# gnuPlot packages
#install_package "python-numpy"
install_package "gnuplot"
install_package "gnuplot-nox"

# SQLite3 support (incl python3)
install_package "sqlite3"

echo; echo "*********************************************************"
python3 -m pip install --upgrade pip setuptools wheel
sudo pip3 install -r requirements.txt

getfilefromserver ".my.kam.cnf" "0740"

commonlibversion=$(pip3 freeze |grep mausy5043 |cut -c 26-)
if [ "${commonlibversion}" != "${required_commonlibversion}" ]; then
  echo; echo "*********************************************************"
  echo "Install common python functions..."
  sudo pip3 uninstall -y mausy5043-common-python
  pushd /tmp || exit 1
    git clone -b "${commonlibbranch}" https://gitlab.com/mausy5043-installer/mausy5043-common-python.git
    pushd /tmp/mausy5043-common-python || exit 1
      sudo ./setup.py install
    popd || exit
    sudo rm -rf mausy5043-common-python/
  popd || exit
  echo
  echo -n "Installed: "
  pip3 freeze | grep mausy5043
  echo
fi

pushd "${HOME}/kamstrupd" || exit 1
  # To suppress git detecting changes by chmod:
  git config core.fileMode false
  # set the branch
  if [ ! -e "${HOME}/.kamstrupd.branch" ]; then
    echo "v4" > "${HOME}/.kamstrupd.branch"
  fi

  # Recover the database from the server
  scripts/kamfile.sh --install

  # Create the /etc/cron.d directory if it doesn't exist
  sudo mkdir -p /etc/cron.d
  # Set up some cronjobs
  echo "# m h dom mon dow user  command" | sudo tee /etc/cron.d/kamstrupd
  echo "#${minit}  * *   *   *   ${ME}    ${HOME}/kamstrupd/update.sh 2>&1 | logger -p info -t kamstrupd" | sudo tee --append /etc/cron.d/kamstrupd
  # @reboot we allow for 10s for the network to come up:
  echo "@reboot               ${ME}    sleep 10; ${HOME}/kamstrupd/update.sh 2>&1 | logger -p info -t kamstrupd" | sudo tee --append /etc/cron.d/kamstrupd
popd || exit


echo; echo "*********************************************************"
echo -n "Finished installation of KAMSTRUPd on "; date
