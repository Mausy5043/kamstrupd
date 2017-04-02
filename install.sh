#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

ME=$(whoami)

echo -n "Started installing KAMSTRUPd on "; date
minit=$(echo $RANDOM/555 |bc)
echo "MINIT = $minit"

install_package()
{
  # See if packages are installed and install them.
  package=$1
  status=$(dpkg-query -W -f='${Status} ${Version}\n' $package 2>/dev/null | wc -l)
  if [ "$status" -eq 0 ]; then
    sudo apt-get -yuV install $package
  fi
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

# MySQL support (python3)
install_package "mysql-client"
install_package "libmysqlclient-dev"
# install_package "python-mysqldb"  # only required by python 2
sudo pip3 install mysqlclient

echo "Install common python functions..."
pushd /tmp
  git clone https://github.com/Mausy5043/mausy5043-common-python.git
  # set permissions
  chmod -R 0755 /tmp/mausy5043-common-python
  pushd /tmp/mausy5043-common-python
    sudo ./setup.py install
  popd
popd

pushd "$HOME/kamstrupd"
  # To suppress git detecting changes by chmod:
  git config core.fileMode false
  # set the branch
  if [ ! -e "$HOME/.kamstrupd.branch" ]; then
    echo "v1" > "$HOME/.kamstrupd.branch"
  fi

  # Create the /etc/cron.d directory if it doesn't exist
  sudo mkdir -p /etc/cron.d
  # Set up some cronjobs
  echo "# m h dom mon dow user  command" | sudo tee /etc/cron.d/kamstrupd
  echo "$minit  * *   *   *   $ME    $HOME/kamstrupd/update.sh 2>&1 | logger -p info -t kamstrupd" | sudo tee --append /etc/cron.d/kamstrupd
  # @reboot we allow for 10s for the network to come up:
  echo "@reboot               $ME    sleep 10; $HOME/kamstrupd/update.sh 2>&1 | logger -p info -t kamstrupd" | sudo tee --append /etc/cron.d/kamstrupd
popd

echo -n "Finished installation of KAMSTRUPd on "; date
