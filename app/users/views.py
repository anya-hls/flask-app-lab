from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from app import db
from app.users import user_bp
from app.users.forms import LoginForm, RegistrationForm
from app.users.models import User


@user_bp.route('/hi/<name>')
def greetings(name):
    age = request.args.get('age', '')
    return render_template(
        'users/hi.html',
        name=name.upper(),
        age=age,
        title='Привітання'
    )


@user_bp.route('/admin')
def admin():
    return redirect(
        url_for('users.greetings', name='Administrator', age=45)
    )


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=User.hash_password(form.password.data)
        )
        db.session.add(user)
        db.session.commit()

        flash(f'Акаунт для {form.username.data} створено!', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/register.html', form=form, title='Реєстрація')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.email == form.email.data))

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Ви успішно увійшли в систему!', 'success')
            return redirect(url_for('users.account'))

        flash('Неправильний email або пароль!', 'danger')

    return render_template('users/login.html', form=form, title='Вхід')


@user_bp.route('/account')
@login_required
def account():
    return render_template('users/account.html', user=current_user, title='Акаунт')


@user_bp.route('/list')
@login_required
def users_list():
    users = db.session.scalars(select(User).order_by(User.id)).all()
    return render_template('users/users_list.html', users=users, title='Користувачі')


@user_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('Ви вийшли із системи.', 'info')
    return redirect(url_for('users.login'))


@user_bp.route('/profile')
@login_required
def profile():
    return render_template(
        'users/profile.html',
        username=current_user.username,
        title='Профіль',
        cookies=request.cookies,
        theme=request.cookies.get('theme', 'light')
    )


@user_bp.route('/profile/cookies/add', methods=['POST'])
@login_required
def add_cookie():
    key = request.form.get('key', '').strip()
    value = request.form.get('value', '')
    max_age = request.form.get('max_age', '')

    if not key or not max_age.isdigit() or int(max_age) <= 0:
        flash('Введіть ключ і правильний термін дії!', 'error')
        return redirect(url_for('users.profile'))

    response = redirect(url_for('users.profile'))
    response.set_cookie(key, value, max_age=int(max_age))
    flash('Cookie успішно додано!', 'success')

    return response


@user_bp.route('/profile/cookies/delete', methods=['POST'])
@login_required
def delete_cookie():
    key = request.form.get('key', '').strip()

    if not key:
        flash('Вкажіть ключ cookie для видалення!', 'error')
        return redirect(url_for('users.profile'))

    response = redirect(url_for('users.profile'))
    response.delete_cookie(key)
    flash('Cookie видалено!', 'success')

    return response


@user_bp.route('/profile/cookies/delete-all', methods=['POST'])
@login_required
def delete_all_cookies():
    response = redirect(url_for('users.profile'))

    for key in request.cookies:
        response.delete_cookie(key)

    flash('Усі cookies видалено!', 'success')

    return response


@user_bp.route('/profile/theme/<theme>', methods=['POST'])
@login_required
def change_theme(theme):
    if theme not in ('light', 'dark'):
        flash('Невідома кольорова схема!', 'error')
        return redirect(url_for('users.profile'))

    response = redirect(url_for('users.profile'))
    response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 30)
    return response
    