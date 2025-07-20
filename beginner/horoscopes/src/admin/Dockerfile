FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY admin.go cert.pem key.pem . 

RUN go build admin.go

# FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-22.04
FROM alpine:latest

WORKDIR /root/
COPY --from=builder /app/admin .

CMD ["./admin"]

# ENV JAIL_CWD=/chal

# COPY ./admin /home/ctf/chal/pwn
# COPY --from=builder /app/admin /home/ctf/chal/pwn
