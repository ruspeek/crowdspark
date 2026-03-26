from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Project, Backer

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация БД
db.init_app(app)

# Создание таблиц при первом запуске (для разработки)
with app.app_context():
    db.create_all()
    # Добавляем тестовые проекты, если база пустая
    if Project.query.count() == 0:
        demo_projects = [
            Project(
                title="3D Теннисный Мяч",
                description="Инновационный мяч с внутренней решетчатой структурой (соты, гироид). Настраиваемая упругость, отскок и износостойкость под конкретного игрока — от новичка до профессионала.",
                category="Стартапы",
                amount_raised=150000,
                goal_amount=500000,
                image_url="https://via.placeholder.com/400x300/1a1a2e/ffffff?text=3D+Tennis+Ball",
                creator_email="demo@tennis.com"
            ),
            Project(
                title="Смарт-зеркала",
                description="Виртуальная примерочная: подбор одежды нужного размера и цвета, создание готового образа без участия консультанта. Технологии из США и Азии теперь доступны вам.",
                category="Технологии",
                amount_raised=320000,
                goal_amount=1000000,
                image_url="https://via.placeholder.com/400x300/1a1a2e/ffffff?text=Smart+Mirrors",
                creator_email="demo@mirrors.com"
            ),
            Project(
                title="DanceConnect",
                description="Маркетплейс для бальных танцев. Единая платформа для поиска и приобретения всего необходимого: от обуви до мастер-классов.",
                category="Приложения",
                amount_raised=50000,
                goal_amount=300000,
                image_url="https://via.placeholder.com/400x300/1a1a2e/ffffff?text=DanceConnect",
                creator_email="demo@dance.com"
            ),
        ]
        db.session.bulk_save_objects(demo_projects)
        db.session.commit()

@app.route('/')
def index():
    """Главная страница с проектами"""
    projects = Project.query.filter_by(status='active').all()
    return render_template('index.html', projects=projects)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    """Страница регистрации нового проекта/компания"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        goal_amount = request.form.get('goal_amount', type=int)
        image_url = request.form.get('image_url')
        creator_email = request.form.get('creator_email')

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
            amount_raised=0
        )

        db.session.add(new_project)
        db.session.commit()

        flash(f'Проект "{title}" успешно зарегистрирован!', 'success')
        return redirect(url_for('index'))

    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Страница конкретного проекта"""
    project = Project.query.get_or_404(project_id)
    return render_template('project.html', project=project)

@app.route('/support/<int:project_id>', methods=['POST'])
def support_project(project_id):
    """Обработка поддержки проекта (Инвестор)"""
    project = Project.query.get_or_404(project_id)
    amount = request.form.get('amount', type=int)
    name = request.form.get('name')
    email = request.form.get('email')

    if not amount or amount < 100:
        flash('Минимальная сумма поддержки — 100 ₽', 'error')
        return redirect(url_for('project_detail', project_id=project_id))

    # Создаем запись о поддержке
    backer = Backer(
        project_id=project_id,
        amount=amount,
        backer_name=name,
        backer_email=email
    )

    # Обновляем сумму сбора
    project.amount_raised += amount

    db.session.add(backer)
    db.session.commit()

    flash(f'Спасибо за поддержку {project.title}!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/api/projects')
def api_projects():
    """API endpoint для получения проектов (JSON)"""
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
            'currency': p.currency
        } for p in projects]
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)