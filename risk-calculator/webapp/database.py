"""
Database initialization and configuration for the Open FAIR Calculator.
"""

import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask application."""
    default_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'fair_calculator.db'
    )
    db_path = os.environ.get('DB_PATH', default_path)
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    uri_path = db_path.replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{uri_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
