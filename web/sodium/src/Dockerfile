FROM python:3.11.3-bullseye

WORKDIR /

RUN apt update &&\
 apt install -y curl gnupg2 ca-certificates lsb-release debian-archive-keyring build-essential libssl-dev wget python3-pip
RUN curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian `lsb_release -cs` nginx" > /etc/apt/sources.list.d/nginx.list && \
    echo "deb-src [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian `lsb_release -cs` nginx" >> /etc/apt/sources.list.d/nginx.list && \
    echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian `lsb_release -cs` nginx" >> /etc/apt/sources.list.d/nginx.list && \
    echo "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" >> /etc/apt/preferences.d/99nginx

RUN apt update && \
    apt install -y nginx libadns1-dev && \
    pip3 install h11==0.15.0 Flask==2.3.3 Flask-SQLAlchemy==3.1.1 requests==2.31.0 python-dotenv==1.1.0

# Configure Pound
WORKDIR /tmp
RUN wget https://github.com/graygnuorg/pound/releases/download/v4.15/pound-4.15.tar.gz && \
    tar -xzf pound-4.15.tar.gz && \
    cd pound* &&\
    ./configure && \
    make && \
    make install && \
    cd .. && rm -rf pound*

# Copy your challenge files
# Add users and directories
RUN useradd -m customerapp && useradd -m rpcservice && \
    mkdir -p /home/customerapp/ && \
    mkdir -p /home/rpcservice/

COPY conf/default.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
COPY rpc_service/ /home/rpcservice/rpc_service/
COPY customer_app/ /home/customerapp/customer_app/
# Configure directory permissions
RUN chmod -R 700 /home/rpcservice/ && \
    chown -R customerapp:customerapp /home/customerapp/ && \
    chown -R rpcservice:rpcservice /home/rpcservice/

COPY conf/pound.cfg /usr/local/etc/pound.cfg
COPY init.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
