FROM golang:1.24.2-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/for_golf_hard main.go

FROM alpine:latest
COPY --from=builder /app/for_golf_hard /for_golf_hard
EXPOSE 10809
ENV FLAG="DUCTF{i_hope_you_learned_a_lot_about_ext4_31890143}"
ENTRYPOINT ["/for_golf_hard", "-listen-nbd", "0.0.0.0:10809", "-nbd-write-limit-per-client", "24576"]
