import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env файла (для локальной разработки)


class Config:
    # База данных Neon
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@ep-xxx.neon.tech/neondb')

    # SQLAlchemy настройки
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Проверка соединения перед использованием
        'connect_args': {'sslmode': 'require'}  # Neon требует SSL
    }

    # Секретный ключ для сессий
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')