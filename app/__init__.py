import logging
import os

from flask import Flask

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'lab5-development-secret-key'
)

app.config['PRODUCTS_DB_PATH'] = os.path.join(
    BASE_DIR,
    'data',
    'products.json'
)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/contact.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

from app import views
from app.users import user_bp
from app.products import products_bp

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(products_bp, url_prefix='/products')

from app.products.database import initialize_database

with app.app_context():
    initialize_database()