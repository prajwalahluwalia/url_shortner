from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "klsgciqegifgelbilug;o"

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost/urlshortener"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from . import urlshort
    app.register_blueprint(urlshort.bp)

    with app.app_context():
        db.create_all()

    return app
