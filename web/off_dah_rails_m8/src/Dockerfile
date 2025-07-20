FROM golang:1.24.4-bookworm AS base

COPY gateway /gateway
WORKDIR /gateway
RUN go build .

FROM ruby:3.4-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
  apt install --no-install-recommends -y lsb-release supervisor mariadb-server redis-server && \
  mkdir /run/mysqld && \
  chown mysql:mysql /run/mysqld/ && \
  rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www && chown www-data:www-data /var/www

WORKDIR /var/www
USER www-data

RUN gem install rails:8.0.2

RUN rails new off_dah_rails_m8 --minimal --api --database=mariadb-mysql --skip-dev --skip-devcontainer --skip-bundle

WORKDIR /var/www/off_dah_rails_m8/

COPY ruby-app/Gemfile ./Gemfile

RUN bundle install

COPY ruby-app/route_create_template.rb route_create_template.rb

RUN ./bin/rails app:template LOCATION=route_create_template.rb

COPY ruby-app/main_controller.rb app/controllers/main_controller.rb

RUN wget -O /var/www/off_dah_rails_m8/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/81b1373f17855a4dc21156cfe1694c31d7d1792e/wait-for-it.sh && \
  echo "b7a04f38de1e51e7455ecf63151c8c7e405bd2d45a2d4e16f6419db737a125d6  /var/www/off_dah_rails_m8/wait-for-it.sh" | sha256sum -c && \
  chmod +x /var/www/off_dah_rails_m8/wait-for-it.sh

COPY --chown=www-data:www-data ruby-app/setup-start.sh /var/www/off_dah_rails_m8/setup-start.sh

RUN chmod +x /var/www/off_dah_rails_m8/setup-start.sh

USER root

RUN find /var/www/ -type f -not -path "./tmp/*" -exec chown root:root {} \;
RUN chmod +r /var/www/off_dah_rails_m8/config/master.key

COPY --from=base /gateway/odr-gateway /gateway/odr-gateway

COPY configs/supervisord.conf /etc/supervisord.conf
COPY configs/redis.conf /etc/redis/redis.conf
COPY redis/redis_init.sh /etc/redis/redis_init.sh
RUN chmod +x /etc/redis/redis_init.sh

# todo add some config files in here
RUN mkdir -p /etc/monke-app-configs/

EXPOSE 3000
ENV RAILS_ENV="production"
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
