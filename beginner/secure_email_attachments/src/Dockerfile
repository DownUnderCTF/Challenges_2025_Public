
FROM golang:1.24.4-bookworm AS base

COPY app /app
WORKDIR /app
RUN go build .

FROM golang:1.24.4-bookworm
COPY --from=base /app/secure-email-attachments /app/secure-email-attachments
COPY --from=base /app/attachments /app/attachments
COPY --from=base /app/flag.txt /etc/flag.txt

USER www-data
WORKDIR /app
ENTRYPOINT [ "/app/secure-email-attachments" ]