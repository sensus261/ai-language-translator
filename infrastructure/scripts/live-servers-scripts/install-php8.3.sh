#!/bin/bash

#########################################################################################################################################
# This script is intended to be used on LIVE servers
# It will install PHP 8.3 and all the necessary extensions
# It will also enable the PHP 8.3 service
# It will guide the developer to update the number of workers and the apache2 sites configuration + also the supervisor configuration
#########################################################################################################################################

# Step 1: Install PHP 8.3
echo -e "\n\n Installing PHP 8.3"

sudo apt install php8.3 php8.3-fpm

a2enmod proxy_fcgi setenvif
sudo a2enconf php8.3-fpm

# Step 2: Enable PHP 8.3 service
echo -e "\n\n Enabling PHP 8.3 service"

sudo systemctl start php8.3-fpm
sudo systemctl enable php8.3-fpm

# Step 3: Install PHP 8.3 extensions
echo -e "\n\n Installing PHP 8.3 extensions"

sudo apt install php8.3-common
sudo apt install php8.3-apcu
sudo apt install php8.3-bz2
sudo apt install php8.3-curl
sudo apt install php8.3-gd
sudo apt install php8.3-igbinary
sudo apt install php8.3-imap
sudo apt install php8.3-intl
sudo apt install php8.3-ldap
sudo apt install php8.3-mbstring
sudo apt install php8.3-mysqli
sudo apt install php8.3-odbc
sudo apt install php8.3-pdo-mysql
sudo apt install php8.3-pdo-odbc
sudo apt install php8.3-pdo-pgsql
sudo apt install php8.3-pgsql
sudo apt install php8.3-redis
sudo apt install php8.3-soap
sudo apt install php8.3-xmlrpc
sudo apt install php8.3-zip
sudo apt install php8.3-dom

# Step 4: Install PHP 8.3 KAFKA extension
sudo apt install -y librdkafka-dev php-dev
sudo apt install -y php-pear
sudo pecl install rdkafka

echo -e "\nextension=rdkafka.so" | sudo tee -a /etc/php/8.3/cli/php.ini
echo -e "\nextension=rdkafka.so" | sudo tee -a /etc/php/8.3/fpm/php.ini

# Step 4: Restart PHP service
echo -e "\n\n Restarting PHP service"

sudo systemctl restart php8.3-fpm
sudo systemctl restart apache2

# Step 5: Success!
echo -e "\n\n\n PHP 8.3 installed successfully!"
echo -e "\n\n Don't forget to: "
echo -e "\n 1. Update the number of workers using 'sudo nano /etc/php/8.3/fpm/pool.d/www.conf' (search for 'pm.max_children') and then restart the service with 'sudo systemctl restart php8.3-fpm'"
echo -e "\n 2. Update the apache2 sites configuration to use the new PHP version. You can find the configuration files at '/etc/apache2/sites-available/'. After configuration is done, you can restart the apache2 service with 'sudo systemctl restart apache2'"
echo -e "\n 3. Update the supervisor comfiguration to use the new PHP version. You can find the configuration files at '/etc/supervisor/conf.d/'. After configuration is done, you can restart the supervisor service with 'sudo supervisorctl reload'"
echo -e "\n 4. Update the crontab configuration to use the new PHP version."
echo -e "\n\n GOOD LUCK!"
