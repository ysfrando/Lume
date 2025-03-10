import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
MESSAGE_EXPIRY = int(os.getenv("MESSAGE_EXPIRY", 60))  # Default 60s
