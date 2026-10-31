from flask import render_template, request, redirect, url_for, session, flash

from app.users import user_bp


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

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == 'admin' and password == '1234':
            session['username'] = username
            flash('Ви успішно увійшли в систему!', 'success')
            return redirect(url_for('users.profile'))

        flash('Неправильний логін або пароль!', 'error')
        return redirect(url_for('users.login'))

    return render_template('users/login.html', title='Вхід')

@user_bp.route('/profile')
def profile():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему!', 'error')
        return redirect(url_for('users.login'))

    return render_template(
        'users/profile.html',
        username=session['username'],
        title='Профіль',
        cookies=request.cookies,
        theme=request.cookies.get('theme', 'light')
    )

@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('Ви вийшли із системи.', 'success')
    return redirect(url_for('users.login'))

@user_bp.route('/profile/cookies/add', methods=['POST'])
def add_cookie():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему!', 'error')
        return redirect(url_for('users.login'))

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
def delete_cookie():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему!', 'error')
        return redirect(url_for('users.login'))

    key = request.form.get('key', '').strip()

    if not key:
        flash('Вкажіть ключ cookie для видалення!', 'error')
        return redirect(url_for('users.profile'))

    response = redirect(url_for('users.profile'))
    response.delete_cookie(key)
    flash('Cookie видалено!', 'success')

    return response


@user_bp.route('/profile/cookies/delete-all', methods=['POST'])
def delete_all_cookies():
    if 'username' not in session:
        flash('Спочатку увійдіть у систему!', 'error')
        return redirect(url_for('users.login'))

    response = redirect(url_for('users.profile'))

    for key in request.cookies:
        response.delete_cookie(key)

    flash('Усі cookies видалено!', 'success')

    return response

@user_bp.route('/profile/theme/<theme>', methods=['POST'])
def change_theme(theme):
    if 'username' not in session:
        flash('Спочатку увійдіть у систему!', 'error')
        return redirect(url_for('users.login'))

    if theme not in ('light', 'dark'):
        flash('Невідома кольорова схема!', 'error')
        return redirect(url_for('users.profile'))

    response = redirect(url_for('users.profile'))
    response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 30)
    return response
