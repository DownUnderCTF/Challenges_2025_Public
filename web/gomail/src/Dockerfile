FROM golang:1.24.4-bookworm AS base

COPY app /app
WORKDIR /app
RUN go build .

FROM golang:1.24.4-bookworm
COPY --from=base /app/gomail /app/gomail

ENTRYPOINT [ "/app/gomail" ]