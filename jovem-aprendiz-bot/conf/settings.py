import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


TWITTER_APP_KEY = os.getenv("TWITTER_APP_KEY")
TWITTER_APP_SECRET = os.getenv("TWITTER_APP_SECRET")
