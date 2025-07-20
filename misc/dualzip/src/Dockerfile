FROM python:3.12-alpine

RUN apk add p7zip unzip zip

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app.py ./
COPY templates ./templates

RUN echo "DUCTF{what_the_z1p_just_happened_38442190}" > /flag

EXPOSE 8000

USER nobody

CMD ["python3", "app.py"]
