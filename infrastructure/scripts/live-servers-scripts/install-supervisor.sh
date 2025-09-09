#!/bin/bash

#########################################################################################################################################
# This script is intended to be used on LIVE servers
# It will install SUPERVISOR
#########################################################################################################################################

# Step 1: Install SUPERVISOR
echo -e "\n\n Installing SUPERVISOR"

sudo apt update
sudo apt install supervisor

# Step 2: Success!
echo -e "\n\n\n Supervisor installed successfully! "
echo -e "\n\n Don't forget to: "
echo -e "\n 1. Update / create the supervisor comfigurations. You can find the configuration files at '/etc/supervisor/conf.d/'. After configuration is done, you can restart the supervisor service with 'sudo supervisorctl reread && sudo supervisorctl reload'"
