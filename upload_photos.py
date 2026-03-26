#!/usr/bin/env python3
"""
Скрипт для загрузки локальных фотографий в проекты
Использование: python upload_photos.py
"""

import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Загружаем переменные окружения
load_dotenv()

# Настройки
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'projects'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Разрешенные расширения
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@ep-xxx.neon.tech/neondb')
engine = create_engine(DATABASE_URL, connect_args={'sslmode': 'require'})
Session = sessionmaker(bind=engine)


def allowed_file(filename):
    """Проверка расширения файла"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def copy_image_to_upload_folder(source_path, project_id):
    """Копирование изображения в папку загрузок"""
    if not os.path.exists(source_path):
        print(f"❌ Файл не найден: {source_path}")
        return None

    if not allowed_file(source_path):
        print(f"❌ Недопустимый формат: {source_path}")
        print(f"   Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")
        return None

    # Генерируем уникальное имя файла
    ext = Path(source_path).suffix.lower()
    filename = f"project_{project_id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = UPLOAD_FOLDER / filename

    try:
        # Копируем файл
        shutil.copy2(source_path, dest_path)
        print(f"✅ Файл скопирован: {filename}")

        # Возвращаем URL для веб-доступа
        return f"/static/uploads/projects/{filename}"
    except Exception as e:
        print(f"❌ Ошибка копирования: {e}")
        return None


def update_project_image(project_id, image_url):
    """Обновление изображения в базе данных"""
    session = Session()
    try:
        # Проверяем существование проекта
        result = session.execute(
            text("SELECT id, title FROM projects WHERE id = :id"),
            {"id": project_id}
        )
        project = result.fetchone()

        if not project:
            print(f"❌ Проект с ID {project_id} не найден!")
            return False

        # Обновляем image_url
        session.execute(
            text("""
                UPDATE projects 
                SET image_url = :image_url 
                WHERE id = :id
            """),
            {"image_url": image_url, "id": project_id}
        )

        session.commit()
        print(f"✅ Проект '{project.title}' обновлен!")
        print(f"   URL: {image_url}")
        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка БД: {e}")
        return False
    finally:
        session.close()


def list_projects():
    """Показать все проекты"""
    session = Session()
    try:
        result = session.execute(text("""
            SELECT id, title, category, image_url 
            FROM projects 
            ORDER BY id
        """))

        projects = result.fetchall()

        print("\n" + "=" * 80)
        print("СУЩЕСТВУЮЩИЕ ПРОЕКТЫ")
        print("=" * 80)

        if not projects:
            print("❌ Проекты не найдены!")
            return []

        for project in projects:
            print(f"\nID: {project.id}")
            print(f"Название: {project.title}")
            print(f"Категория: {project.category}")
            print(f"Изображение: {project.image_url or 'НЕ УСТАНОВЛЕНО'}")
            print("-" * 80)

        return projects
    finally:
        session.close()


def upload_photo_interactive():
    """Интерактивный режим загрузки"""
    print("\n" + "=" * 80)
    print("ЗАГРУЗКА ФОТОГРАФИЙ В ПРОЕКТЫ")
    print("=" * 80)

    # Показываем проекты
    projects = list_projects()

    if not projects:
        print("\n❌ Сначала создайте проекты!")
        return

    print("\n" + "=" * 80)
    print("ИНСТРУКЦИЯ:")
    print("1. Скопируйте ваши фото в папку проекта или укажите полный путь")
    print("2. Введите ID проекта и путь к фото")
    print("=" * 80)

    while True:
        print("\nДействия:")
        print("1. Загрузить фото для проекта")
        print("2. Показать проекты")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == '0':
            print("👋 Готово!")
            break

        elif choice == '1':
            # Ввод ID
            project_id = input("Введите ID проекта: ").strip()
            try:
                project_id = int(project_id)
            except ValueError:
                print("❌ ID должен быть числом!")
                continue

            # Ввод пути к фото
            photo_path = input("Введите путь к фотографии: ").strip()
            photo_path = photo_path.strip('"\'')  # Убираем кавычки если есть

            # Копируем фото
            image_url = copy_image_to_upload_folder(photo_path, project_id)

            if image_url:
                # Обновляем БД
                if update_project_image(project_id, image_url):
                    print("✅ Фото загружено успешно!")
                else:
                    print("❌ Ошибка обновления БД")
            else:
                print("❌ Ошибка загрузки фото")

        elif choice == '2':
            list_projects()

        else:
            print("❌ Неверный выбор")


def upload_photos_batch(photos_dict):
    """
    Массовая загрузка фото
    photos_dict: {project_id: "path/to/photo.jpg"}
    """
    print("\n" + "=" * 80)
    print("МАССОВАЯ ЗАГРУЗКА ФОТОГРАФИЙ")
    print("=" * 80)

    success_count = 0
    for project_id, photo_path in photos_dict.items():
        print(f"\n[{project_id}] {photo_path}")

        image_url = copy_image_to_upload_folder(photo_path, project_id)
        if image_url:
            if update_project_image(project_id, image_url):
                success_count += 1

    print("\n" + "=" * 80)
    print(f"ГОТОВО! Загружено {success_count} из {len(photos_dict)} фото")
    print("=" * 80)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Командный режим: python upload_photos.py <project_id> <photo_path>
        if len(sys.argv) == 3:
            try:
                project_id = int(sys.argv[1])
                photo_path = sys.argv[2]

                image_url = copy_image_to_upload_folder(photo_path, project_id)
                if image_url:
                    update_project_image(project_id, image_url)
            except ValueError:
                print("❌ Первый аргумент должен быть числом (ID проекта)")
                sys.exit(1)
        else:
            print("Использование:")
            print("  python upload_photos.py                           # Интерактивный режим")
            print("  python upload_photos.py <id> <путь_к_фото>        # Загрузить одно фото")
            print("\nПример:")
            print("  python upload_photos.py 1 /Users/stepan/Pictures/dance.jpg")
            print("  python upload_photos.py 2 ~/Downloads/mirror.png")
    else:
        # Интерактивный режим
        upload_photo_interactive()