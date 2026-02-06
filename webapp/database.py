"""
Database initialization and configuration for the Open FAIR Calculator.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask application."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fair_calculator.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
