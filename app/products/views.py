
import os
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
    request
)
from werkzeug.utils import secure_filename

from app.products import products_bp
from app.products.forms import ProductForm
from app.products.database import (
    get_all_products,
    get_product,
    add_product,
    update_product,
    delete_product
)


def save_image(image):
    if not image or not image.filename:
        return ''

    extension = Path(secure_filename(image.filename)).suffix.lower()
    filename = f'{uuid.uuid4().hex}{extension}'

    upload_folder = os.path.join(
        current_app.root_path,
        'products',
        'static',
        'uploads'
    )

    os.makedirs(upload_folder, exist_ok=True)
    image.save(os.path.join(upload_folder, filename))

    return f'uploads/{filename}'


def remove_image(image_path):
    if not image_path:
        return

    upload_folder = os.path.abspath(
        os.path.join(
            current_app.root_path,
            'products',
            'static'
        )
    )

    file_path = os.path.abspath(
        os.path.join(upload_folder, image_path)
    )

    if os.path.commonpath([upload_folder, file_path]) == upload_folder:
        if os.path.isfile(file_path):
            os.remove(file_path)


def get_form_data(form, image_path=''):
    return {
        'name': form.name.data.strip(),
        'content': form.content.data.strip(),
        'price': str(Decimal(form.price.data).quantize(Decimal('0.01'))),
        'category': form.category.data,
        'quantity': form.quantity.data,
        'image': image_path,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }


@products_bp.route('/')
def product_list():
    products = get_all_products()

    return render_template(
        'products/products.html',
        products=products,
        title='Товари'
    )


@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    return render_template(
        'products/detail_product.html',
        product=product,
        title=product['name']
    )


@products_bp.route('/add', methods=['GET', 'POST'])
def product_add():
    form = ProductForm()

    if form.validate_on_submit():
        image_path = save_image(form.image.data)
        product_data = get_form_data(form, image_path)

        add_product(product_data)

        flash('Товар успішно додано!', 'success')
        return redirect(url_for('products.product_list'))

    return render_template(
        'products/product_form.html',
        form=form,
        title='Додавання товару',
        heading='Додати товар'
    )


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def product_edit(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    form = ProductForm()

    if request.method == 'GET':
        form.name.data = product['name']
        form.content.data = product['content']
        form.price.data = Decimal(str(product['price']))
        form.category.data = product['category']
        form.quantity.data = product['quantity']

    if form.validate_on_submit():
        image_path = product.get('image', '')

        if form.image.data and form.image.data.filename:
            new_image_path = save_image(form.image.data)

            if new_image_path:
                remove_image(image_path)
                image_path = new_image_path

        product_data = get_form_data(form, image_path)
        product_data['created_at'] = product['created_at']

        update_product(product_id, product_data)

        flash('Товар успішно оновлено!', 'success')

        return redirect(
            url_for('products.product_detail', product_id=product_id)
        )

    return render_template(
        'products/product_form.html',
        form=form,
        title='Редагування товару',
        heading='Редагувати товар',
        product=product
    )


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
def product_delete(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    delete_product(product_id)
    remove_image(product.get('image', ''))

    flash('Товар успішно видалено!', 'success')

    return redirect(url_for('products.product_list'))
