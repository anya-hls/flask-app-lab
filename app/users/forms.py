from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError
)

from app import db
from app.users.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[
        DataRequired(message='Введіть ім\'я користувача.'),
        Length(min=4, max=14, message='Довжина має бути від 4 до 14 символів.'),
        Regexp(
            r'^[A-Za-z][A-Za-z0-9_.]*$',
            message='Ім\'я має починатися з літери і містити лише літери, цифри, крапки або підкреслення.'
        )
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Введіть email.'),
        Email(message='Невірний формат email.')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введіть пароль.'),
        Length(min=6, message='Пароль має бути не коротшим за 6 символів.')
    ])

    confirm_password = PasswordField('Підтвердіть пароль', validators=[
        DataRequired(message='Підтвердіть пароль.'),
        EqualTo('password', message='Паролі не збігаються.')
    ])

    submit = SubmitField('Зареєструватися')

    def validate_username(self, username):
        user = db.session.scalar(select(User).where(User.username == username.data))
        if user:
            raise ValidationError('Користувач з таким іменем уже існує.')

    def validate_email(self, email):
        user = db.session.scalar(select(User).where(User.email == email.data))
        if user:
            raise ValidationError(f'Користувач з email {email.data} уже існує.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Введіть email.'),
        Email(message='Невірний формат email.')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введіть пароль.')
    ])
    remember = BooleanField('Запам\'ятати мене')
    submit = SubmitField('Увійти')
    