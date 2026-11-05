
import logging
import os

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'lab5-development-secret-key'
)

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
