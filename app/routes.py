import os
from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, CourseForm, ReminderForm, NotificationSettingsForm
from models import db, User, Course, Reminder
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
@app.route('/courses/<int:page>', methods=['GET'])
def courses(page=1):
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    user_courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.start_date).paginate(page=page, per_page=5)
    return render_template('courses.html', courses=user_courses)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
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
    if form.validate_on_submit():
        if course is None:
            course = Course(user_id=current_user.id)
        form.populate_obj(course)
        db.session.add(course)
        db.session.commit()
        flash('Курс успешно сохранен.')
        return redirect(url_for('courses'))
    return render_template('manage_course.html', form=form, is_new=(course_id is None))

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
    user_reminders = Reminder.query.filter(Reminder.user_id == current_user.id).order_by(Reminder.time).paginate(page=page, per_page=5)
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
