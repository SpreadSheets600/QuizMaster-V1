import os
from flask import Flask
from werkzeug.security import generate_password_hash

from models.database import db
from models.models import User, Subject, Chapter, Quiz, Question, Score

app = None


def create_app():
    app = Flask(__name__)
    app.debug = True

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_master.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SECRET_KEY"] = "secretquizmaster"

    db.init_app(app)
    app.app_context().push()

    db.create_all()

    initialize_db()

    return app


def initialize_db():
    if User.query.count() == 0:
        admin_user = User(
            username="admin",
            password=generate_password_hash("admin"),
            full_name="Administrator",
            role="admin",
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin User Created")


app = create_app()

if __name__ == "__main__":
    app.run()
