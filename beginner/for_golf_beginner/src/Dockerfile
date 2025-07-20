FROM golang:1.24.2-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/for_golf_beginner main.go

FROM alpine:latest
COPY --from=builder /app/for_golf_beginner /for_golf_beginner
EXPOSE 10809
ENV FLAG="DUCTF{now_you_know_how_to_use_nbd_4y742rr2}"
ENTRYPOINT ["/for_golf_beginner", "-listen-nbd", "0.0.0.0:10809"]
