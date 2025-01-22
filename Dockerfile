FROM python:3.11

WORKDIR /app

COPY src/ /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "bot.py"]
