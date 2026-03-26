import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Config:
    # База данных Neon
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@ep-xxx.neon.tech/neondb')

    # SQLAlchemy настройки
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'sslmode': 'require'}
    }

    # Секретный ключ
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # Настройки загрузки файлов
    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'projects'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Максимальный размер файла 16MB

    # Разрешённые расширения
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Создаём папку для загрузок если не существует
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)