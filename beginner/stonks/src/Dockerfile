FROM python:3.12

COPY app /app
WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "/app/stonks.py" ]