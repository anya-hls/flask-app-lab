import logging

from flask import Blueprint, render_template, redirect, url_for, flash

from app.forms import ContactForm

main_bp = Blueprint('main', __name__)

logger = logging.getLogger(__name__)


@main_bp.route('/')
def home():
    return render_template('homepage.html', title='Головна')


@main_bp.route('/resume')
def resume():
    return render_template('resume.html', title='Резюме')


@main_bp.route('/contacts', methods=['GET', 'POST'])
@main_bp.route('/contact', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            logger.info(
                'Contact form submission: name=%s, email=%s, subject=%s, message=%s',
                form.name.data,
                form.email.data,
                form.subject.data,
                form.message.data
            )

            flash('Ваше повідомлення успішно надіслано!', 'success')
            return redirect(url_for('main.contacts'))

        except Exception:
            logger.exception('Failed to save contact form submission')
            flash('Не вдалося зберегти ваше повідомлення.', 'error')

    elif form.is_submitted():
        flash(
            'Не вдалося надіслати повідомлення. Перевірте правильність заповнення форми.',
            'error'
        )

    return render_template(
        'contacts.html',
        form=form,
        title='Контакти'
    )
