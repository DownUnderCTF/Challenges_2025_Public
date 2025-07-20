#!/bin/bash

mysql -u root -e "CREATE DATABASE off_dah_rails_m8_production;"
mysql -u root -D 'off_dah_rails_m8_production' -e "CREATE TABLE flag (flag varchar(255)); INSERT INTO flag VALUES ('${FLAG}');"
mysql -u root -e "CREATE USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}'; GRANT SELECT ON off_dah_rails_m8_production.* TO '${DB_USER}'@'localhost'; FLUSH PRIVILEGES;"
unset FLAG;

su -p -s /bin/bash www-data -c 'export HOME=/var/www && bash -c "/var/www/off_dah_rails_m8/bin/rails server --binding=0.0.0.0"'