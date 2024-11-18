from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Таблица курсов
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    medication = db.Column(db.String(256))
    dosage = db.Column(db.Text)
    start = db.Column(db.Date)
    frequency = db.Column(db.Integer, nullable=False, default=1)  # Частота в днях
    end_date = db.Column(db.Date)
    times_per_day = db.Column(db.Integer)
    next_reminder = db.Column(db.PickleType)  # Здесь Reminder сохраняется как объект
    edited_reminders = db.Column(db.PickleType)  # Хэш-таблица {номер -> Reminder}
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('courses', lazy=True))
    notifications = db.relationship('Notification', backref='course', lazy=True)
# Таблица времени приема
class TimeToTake(db.Model):
    __tablename__ = 'time_to_take'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)

    course = db.relationship('Course', backref=db.backref('times', lazy=True))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

