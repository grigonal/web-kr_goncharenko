from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from forms import *
from datetime import datetime, timedelta
from models import db, User, Course, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask_mail import Mail, Message
from flask import current_app



app = Flask(__name__)
application = app
scheduler = BackgroundScheduler()
app.config.from_object('config.Config')

def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.user_loader(load_user)
Bootstrap(app)
with app.app_context():
    db.create_all()



def send_notification(course_id, time):
    with app.app_context():
        course = Course.query.get(course_id)
        user = course.user  # Assuming `user` relationship exists in the `Course` model
        
        if user and course:
            # Flash a message (this will display as a notification in the app)
            print(f"In-app notification for {user.username}: {course.medication} at {time}")

def schedule_notifications():
    with app.app_context():
        """ This function checks for any scheduled notifications and sends them out at the correct time. """
        notifications = Notification.query.all()
        now = datetime.now()

        for notification in notifications:
            notification_time = datetime.combine(now.date(), notification.time)
            if notification_time <= now:  # If the current time is greater than or equal to the scheduled time
                send_notification(notification.course_id, notification.time)
                # Optionally, you could delete or mark the notification as sent.
                db.session.delete(notification)
                db.session.commit()

# Schedule the notification check to run every minute
scheduler.add_job(func=schedule_notifications, trigger='interval', minutes=1)
scheduler.start()



@app.route('/')
@app.route('/courses/<int:page>', methods=['GET'])
def courses(page=1):
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    user_courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.start).paginate(page=page, per_page=5)
    return render_template('courses.html', courses=user_courses)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.is_submitted():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('courses'))
        flash('Неверное имя пользователя или пароль.')
    return render_template('login.html', form=form)

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('login'))

# Добавление или редактирование курса
@app.route('/courses/new', methods=['GET', 'POST'])
@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def manage_course(course_id=None):
    course = Course.query.get(course_id) if course_id else None
    form = CourseForm(obj=course)
    
    if request.method == 'POST':
        notification_keys = [key for key in request.form.keys() if key.startswith('notifications-') and key.endswith('-time')]
        num_notifications = len(notification_keys)

        # Увеличиваем длину FieldList до количества отправленных полей
        while len(form.notifications) < num_notifications:
            form.notifications.append_entry()

    if form.is_submitted():
        if course is None:
            course = Course(
                medication=form.medication.data,
                dosage=form.dosage.data,
                start=form.start.data,
                frequency=form.frequency.data,
                end_date=form.end_date.data,
                times_per_day=form.times_per_day.data,
                user_id=current_user.id
            )
            db.session.add(course)
            db.session.flush()
        course.medication = form.medication.data
        course.dosage = form.dosage.data
        course.start = form.start.data
        course.frequency = form.frequency.data
        course.end_date = form.end_date.data
        course.times_per_day = form.times_per_day.data

        # Handle notifications (adding, updating, or deleting)
        existing_notifications = {n.id: n for n in course.notifications}
        submitted_notifications = []

        # Process the submitted notification times
        for notification_form in form.notifications:
            if notification_form.time.data:
                submitted_notifications.append(notification_form.time.data)

        # Remove notifications that were deleted
        for notification_id, notification in existing_notifications.items():
            if notification.time not in submitted_notifications:
                db.session.delete(notification)

        # Add new notifications
        for time in submitted_notifications:
            if not any(n.time == time for n in existing_notifications.values()):
                new_notification = Notification(time=time, course_id=course.id)
                db.session.add(new_notification)

        db.session.commit()
        flash('Course successfully saved/updated!')
        return redirect(url_for('courses'))
    return render_template('add_edit_course.html', form=form, is_new=(course_id is None))

# Удаление курса
@app.route('/courses/delete/<int:course_id>', methods=['GET'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        flash('Вы не можете удалить этот курс.')
        return redirect(url_for('courses'))
    db.session.delete(course)
    db.session.commit()
    flash('Курс удален.')
    return redirect(url_for('courses'))

# Напоминания
@app.route('/reminders/<int:page>', methods=['GET'])
@login_required
def reminders(page=1):
    user_reminders = Notification.query.filter(Notification.user_id == current_user.id).order_by(Reminder.time).paginate(page=page, per_page=5)
    return render_template('reminders.html', reminders=user_reminders)

# Изменение настроек уведомлений
@app.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def notification_settings():
    form = NotificationSettingsForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash('Настройки уведомлений обновлены.')
        return redirect(url_for('courses'))
    return render_template('notification_settings.html', form=form)



if __name__ == "__main__":
    app.run(debug=True, port=5001)