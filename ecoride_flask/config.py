import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_NAME = "session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"


db_config = {
    "min_conn": int(os.getenv("DB_POOL_MIN_CONN", 1)),
    "max_conn": int(os.getenv("DB_POOL_MAX_CONN", 10)),
    "db_user": os.getenv("DB_USER"),
    "db_password": os.getenv("DB_PASSWORD"),
    "db_host": os.getenv("DB_HOST"),
    "db_port": os.getenv("DB_PORT"),
    "db_name": os.getenv("DB_NAME"),
}
