FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY Prerequisites/HTTPWebServer /app

EXPOSE 8000 8001 8002
EXPOSE 3000 3001 3002 3003 3004 3005

CMD ["python", "-u", "start_servers.py"]
