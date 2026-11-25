from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SelectMultipleField,
    SubmitField
)
from wtforms.validators import DataRequired, Length

from app import db
from app.users.models import User
from app.posts.models import Tag


class PostForm(FlaskForm):
    title = StringField(
        'Заголовок',
        validators=[
            DataRequired(message='Введіть заголовок.'),
            Length(max=150)
        ]
    )

    content = TextAreaField(
        'Текст допису',
        validators=[
            DataRequired(message='Введіть текст допису.')
        ]
    )

    is_active = BooleanField('Активний допис', default=True)

    publish_date = DateTimeLocalField(
        'Дата публікації',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='Вкажіть дату публікації.')]
    )

    category = SelectField(
        'Категорія',
        choices=[
            ('news', 'Новини'),
            ('publication', 'Публікації'),
            ('tech', 'Технології'),
            ('other', 'Інше')
        ],
        validators=[DataRequired(message='Оберіть категорію.')]
    )

    author_id = SelectField('Автор', coerce=int)

    tags = SelectMultipleField('Теги', coerce=int)

    submit = SubmitField('Зберегти')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = db.session.scalars(select(User).order_by(User.id)).all()
        self.author_id.choices = [(u.id, u.username) for u in users]
        tags = db.session.scalars(select(Tag).order_by(Tag.name)).all()
        self.tags.choices = [(t.id, t.name) for t in tags]
        