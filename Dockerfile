FROM python:3.10

WORKDIR /app

COPY src/ /app/src/
COPY sessions.txt .
COPY main.py .
COPY .env .

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]