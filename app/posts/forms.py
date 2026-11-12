from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SubmitField
)
from wtforms.validators import DataRequired, Length


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

    submit = SubmitField('Зберегти')
