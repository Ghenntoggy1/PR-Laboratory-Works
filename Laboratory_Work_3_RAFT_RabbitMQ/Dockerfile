FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY Prerequisites/HTTPWebServer /app

EXPOSE 8000 8001 8002

CMD ["python", "-u", "start_servers.py"]
