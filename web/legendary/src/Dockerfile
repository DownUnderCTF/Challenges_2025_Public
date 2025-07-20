FROM php:8.4-fpm

RUN apt-get update && \
  apt-get install -y nginx mariadb-server && \
  rm /var/www/html/index.nginx-debian.html && \
  apt-get clean
RUN docker-php-ext-install pdo_mysql

COPY entrypoint.sh /
COPY flag.txt /
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir /var/www/db && chown -R www-data /var/www
COPY setup.sql /setup.sql
COPY www/ /var/www/html

RUN service mariadb start && \
    mysql -e "CREATE DATABASE animals;" && \
    mysql -e "CREATE USER 'user'@'localhost' IDENTIFIED BY 'pass';" && \
    mysql -e "GRANT SELECT ON animals.* TO 'user'@'localhost';" && \
    mysql -e "FLUSH PRIVILEGES;" && \
    mysql animals < /setup.sql && \
    sleep 1 && \
    service mariadb stop

RUN sed -i "s/CHANGEME/$(tr -cd 0-9a-f < /dev/urandom | head -c 32)/" /var/www/html/config.php
RUN mv /flag.txt /flag-$(tr -cd 0-9a-f < /dev/urandom | head -c 32).txt
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

ENTRYPOINT ["bash", "/entrypoint.sh"]