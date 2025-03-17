from flask_login import LoginManager
from flask import Flask, render_template
from werkzeug.security import generate_password_hash

from models.database import db
from models.models import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.debug = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'secretquizmaster'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        initialize_db()

    from controllers.auth import auth_bp
    from controllers.user import user_bp
    from controllers.admin import admin_bp
    from controllers.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    def register_error_handlers(app):
        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('errors/404.html'), 404

        @app.errorhandler(500)
        def server_error(e):
            return render_template('errors/500.html'), 500

    register_error_handlers(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def initialize_db():
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin'),
            email='admin@quizmaster.com',
            full_name='Administrator',
            role='admin',
        )
        db.session.add(admin_user)
        db.session.commit()
        print('Admin User Created')


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
