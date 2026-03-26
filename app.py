import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from config import Config
from models import db, Project, Backer

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация БД
db.init_app(app)


def allowed_file(filename):
    """Проверка расширения файла"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_upload_file(file):
    """Сохранение загруженного файла"""
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        # Путь для сохранения
        upload_path = app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_path, filename)

        # Сохраняем файл
        file.save(filepath)

        # Возвращаем URL для доступа к файлу
        return f"/static/uploads/projects/{filename}"
    return None


# Создание таблиц и тестовых данных
with app.app_context():
    db.create_all()

    if Project.query.count() == 0:
        demo_projects = [
            Project(
                title="3D Теннисный Мяч",
                description="Инновационный мяч с внутренней решетчатой структурой (соты, гироид). Настраиваемая упругость, отскок и износостойкость под конкретного игрока.",
                category="Стартапы",
                amount_raised=150000,
                goal_amount=500000,
                image_url="https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&h=600&fit=crop",
                creator_email="demo@tennis.com"
            ),
            Project(
                title="Смарт-зеркала",
                description="Виртуальная примерочная: подбор одежды нужного размера и цвета, создание готового образа без участия консультанта.",
                category="Технологии",
                amount_raised=320000,
                goal_amount=1000000,
                image_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&h=600&fit=crop",
                creator_email="demo@mirrors.com"
            ),
            Project(
                title="DanceConnect",
                description="Маркетплейс для бальных танцев. Единая платформа для поиска и приобретения всего необходимого.",
                category="Приложения",
                amount_raised=50000,
                goal_amount=300000,
                image_url="https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=800&h=600&fit=crop",
                creator_email="demo@dance.com"
            ),
            Project(
                title="EcoBottle",
                description="Умная бутылка для воды с отслеживанием потребления жидкости и напоминаниями.",
                category="Стартапы",
                amount_raised=80000,
                goal_amount=250000,
                image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&h=600&fit=crop",
                creator_email="demo@ecobottle.com"
            ),
        ]
        db.session.bulk_save_objects(demo_projects)
        db.session.commit()


@app.route('/')
def index():
    projects = Project.query.filter_by(status='active').all()
    return render_template('index.html', projects=projects)


@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        goal_amount = request.form.get('goal_amount', type=int)
        creator_email = request.form.get('creator_email')
        project_url = request.form.get('project_url')

        # Обработка загрузки файла
        image_file = request.files.get('image')
        image_url = None

        if image_file and image_file.filename:
            image_url = save_upload_file(image_file)
        else:
            # Если файл не загружен, используем URL из формы
            image_url = request.form.get('image_url')

        if not title or not goal_amount or not creator_email:
            flash('Заполните обязательные поля: Название, Цель сбора и Email', 'error')
            return redirect(url_for('create_project'))

        new_project = Project(
            title=title,
            description=description,
            category=category,
            goal_amount=goal_amount,
            image_url=image_url,
            creator_email=creator_email,
            project_url=project_url,
            amount_raised=0
        )

        db.session.add(new_project)
        db.session.commit()

        flash(f'Проект "{title}" успешно зарегистрирован!', 'success')
        return redirect(url_for('index'))

    return render_template('create_project.html')


@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project.html', project=project)


@app.route('/support/<int:project_id>', methods=['POST'])
def support_project(project_id):
    project = Project.query.get_or_404(project_id)
    amount = request.form.get('amount', type=int)
    name = request.form.get('name')
    email = request.form.get('email')

    if not amount or amount < 100:
        flash('Минимальная сумма поддержки — 100 ₽', 'error')
        return redirect(url_for('project_detail', project_id=project_id))

    backer = Backer(
        project_id=project_id,
        amount=amount,
        backer_name=name,
        backer_email=email
    )

    project.amount_raised += amount

    db.session.add(backer)
    db.session.commit()

    flash(f'Спасибо за поддержку {project.title}!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/api/projects')
def api_projects():
    projects = Project.query.filter_by(status='active').all()
    return {
        'projects': [{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'category': p.category,
            'raised': p.amount_raised,
            'goal': p.goal_amount,
            'progress': p.progress_percent(),
            'currency': p.currency,
            'image_url': p.image_url
        } for p in projects]
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)