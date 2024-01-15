FROM python:3.10

WORKDIR /app

COPY userbot_global.py .
COPY userbot_settings.py .
COPY sessions.txt .

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "userbot_global.py"]