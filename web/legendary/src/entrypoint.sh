#!/usr/bin/env bash
service mariadb start
service nginx start
exec php-fpm