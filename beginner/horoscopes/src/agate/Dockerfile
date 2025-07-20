FROM rust:latest

RUN cargo install agate

WORKDIR /var/agate

COPY content /var/agate/content

ENTRYPOINT ["agate"]
