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
install_package "git"
install_package "python3"
install_package "mysql-client"
install_package "python-mysqldb"
#install_package "python-numpy"

pushd "$HOME/kamstrupd"
  # To suppress git detecting changes by chmod:
  git config core.fileMode false
  # set the branch
  if [ ! -e "$HOME/.kamstrupd.branch" ]; then
    echo "master" > "$HOME/.kamstrupd.branch"
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
