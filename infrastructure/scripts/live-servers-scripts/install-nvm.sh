#!/bin/bash

#########################################################################################################################################
# This script is intended to be used on LIVE servers
# It will install NVM and the latest node versions
#########################################################################################################################################

# Step 1: Install NVM
echo -e "\n\n Installing NVM"

if command_output=$(nvm --version 2>&1 | grep 'not found'); then
    sudo apt install curl
    curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
    source ~/.bashrc
    nvm install node
    sudo apt-get install npm
    npm install -g yarn
else
    echo -e "\n\n NVM is already installed. Proceeding to install the latest node versions... \n"
fi

nvm install lts/iron
nvm install lts/jod

# Step 2: Success!
echo -e "\n\n\n NVM installed successfully!"
