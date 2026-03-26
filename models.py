from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Стартапы, Технологии, и т.д.

    # Финансы
    amount_raised = db.Column(db.Integer, default=0)  # в копейках/центах
    goal_amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default='RUB')

    # Статус
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ссылки и медиа
    image_url = db.Column(db.String(500))
    project_url = db.Column(db.String(500))

    # Контакты создателя (для регистрации компании/проекта)
    creator_email = db.Column(db.String(120), nullable=True)

    def progress_percent(self):
        """Процент сбора средств"""
        if self.goal_amount == 0:
            return 0
        return min(100, round((self.amount_raised / self.goal_amount) * 100))

    def format_money(self, amount):
        """Форматирование суммы"""
        return f"{amount:,} {self.currency}".replace(',', ' ')

    def __repr__(self):
        return f'<Project {self.title}>'


class Backer(db.Model):
    """Таблица для тех, кто поддерживает проекты"""
    __tablename__ = 'backers'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    backer_name = db.Column(db.String(100))
    backer_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('backers', lazy=True))