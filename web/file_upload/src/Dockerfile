FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

RUN apk add supervisor file
RUN pip install flask requests

COPY appupload.py appview.py ./
COPY templates/ templates/

RUN mkdir /app/uploads && \
    echo 'DUCTF{what_the_javascript_36c66a87dc64c3c591202}' > /app/uploads/8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918-$(xxd -p -l 30 /dev/urandom)

COPY supervisord.conf /etc/supervisord.conf

EXPOSE 5000
EXPOSE 9000

CMD ["/usr/bin/supervisord"]
