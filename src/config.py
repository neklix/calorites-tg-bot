import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
TRAIN_TOKEN = os.getenv("TRAIN_TOKEN")

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN must be set")
if WEATHER_TOKEN is None:
    raise ValueError("WEATHER_TOKEN must be set")
if TRAIN_TOKEN is None:
    raise ValueError("TRAIN_TOKEN must be set")
