FROM python:3.11-slim

WORKDIR /ctf
COPY main-app/ .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 1337

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=1337

CMD ["flask", "run", "--host=0.0.0.0", "--port=1337"]