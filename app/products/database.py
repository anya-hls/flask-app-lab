from pathlib import Path

from flask import current_app
from tinydb import TinyDB, Query


def get_database_path():
    return current_app.config['PRODUCTS_DB_PATH']


def initialize_database(db_path=None):
    path = Path(db_path or get_database_path())
    path.parent.mkdir(parents=True, exist_ok=True)

    db = TinyDB(path)
    table = db.table('products')

    if not table.all():
        table.insert_multiple([
            {
                'id': 1,
                'name': 'Laptop',
                'content': 'Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам’яті та SSD на 512 ГБ.',
                'price': '1200.00',
                'category': 'electronics',
                'quantity': 5,
                'image': '',
                'created_at': '2026-11-05'
            },
            {
                'id': 2,
                'name': 'Phone',
                'content': 'Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год.',
                'price': '800.00',
                'category': 'electronics',
                'quantity': 10,
                'image': '',
                'created_at': '2026-11-05'
            },
            {
                'id': 3,
                'name': 'PC',
                'content': 'Настільний комп’ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD.',
                'price': '1800.00',
                'category': 'electronics',
                'quantity': 3,
                'image': '',
                'created_at': '2026-11-05'
            }
        ])

    db.close()


def get_all_products():
    db = TinyDB(get_database_path())
    products = db.table('products').all()
    db.close()

    return sorted(products, key=lambda product: product['id'])


def get_product(product_id):
    db = TinyDB(get_database_path())
    product = db.table('products').get(
        Query().id == product_id
    )
    db.close()

    return product


def add_product(product_data):
    db = TinyDB(get_database_path())
    table = db.table('products')

    existing_ids = [product['id'] for product in table.all()]
    product_data['id'] = max(existing_ids, default=0) + 1

    table.insert(product_data)
    db.close()

    return product_data


def update_product(product_id, product_data):
    db = TinyDB(get_database_path())
    table = db.table('products')

    table.update(
        product_data,
        Query().id == product_id
    )

    db.close()


def delete_product(product_id):
    db = TinyDB(get_database_path())
    table = db.table('products')

    table.remove(Query().id == product_id)

    db.close()
    