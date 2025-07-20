FROM node:latest AS frontend

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---
FROM python:3.13-slim

WORKDIR /app
COPY ./backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./backend ./
COPY --from=frontend /frontend/dist /app/dist

ENV SECRET=DONTUSEECBPLEASE
EXPOSE 1337
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1337"]
