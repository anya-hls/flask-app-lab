from flask import Flask

app = Flask(__name__)
app.secret_key = 'your-secret-key'

from app import views
from app.users import user_bp
from app.products import products_bp

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(products_bp, url_prefix='/products')
