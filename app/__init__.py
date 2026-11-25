import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.config import config


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])

    os.makedirs(app.instance_path, exist_ok=True)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app.config['PRODUCTS_DB_PATH'] = os.path.join(
        base_dir,
        'data',
        'products.json'
    )
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

    os.makedirs(os.path.join(base_dir, 'logs'), exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(base_dir, 'logs', 'contact.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from app.views import main_bp
    from app.users import user_bp
    from app.products import products_bp
    from app.posts import posts_bp
    from app.posts.models import Post
    from app.products import models as products_models
    from app.users.models import User

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(posts_bp)

    from app.products.database import initialize_database

    with app.app_context():
        initialize_database()

    @app.errorhandler(404)
    def page_not_found(error):
        return 'Сторінку не знайдено', 404

    return app


app = create_app()
