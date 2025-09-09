#!/bin/bash

#########################################################################################################################################
# This script is intended to be used on LIVE servers
# It will install Apache2
#########################################################################################################################################

# Step 1: Install Apache2
echo -e "\n\n Installing Apache2"

if [ -z "$(which apache2)" ]; then
    sudo apt install apache2
    sudo systemctl enable apache2

    sudo a2enmod proxy_wstunnel
    sudo a2enmod rewrite
    sudo a2enmod ssl
    sudo a2enmod headers
else
    echo -e "\n\n Apache2 is already installed. Proceeding to restart the service... \n"
fi

# Step 2: Restart PHP service
echo -e "\n\n Restarting Apache2 service"

sudo systemctl restart apache2

# Step 3: Success!
echo -e "\n\n\n Apache2 installed successfully!"
echo -e "\n\n Don't forget to: "
echo -e "\n 1. Install a php version that you want and configure the sites to use it"
echo -e "\n\n GOOD LUCK!"
