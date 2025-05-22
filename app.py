from flask import Flask, render_template
import os
from dotenv import load_dotenv
load_dotenv()

from extensions import db, login_manager, ckeditor, bootstrap, gravatar # This is fine
from blog_project.main import blog_bp # Changed from relative to absolute
from blog_project.models import User # Changed from relative to absolute, Needed for user_loader

def create_app():
    app = Flask(__name__)

    # Configuration
    # Use a unique secret key for your main application, load from environment
    # app.config['SECRET_KEY'] = os.environ.get('MAIN_APP_SECRET_KEY', 'your_main_app_default_secret_key')
    app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
    # Centralized database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Point login_view to the login route within the 'blog' blueprint
    login_manager.login_view = 'blog.login'
    login_manager.login_message_category = 'info' # Optional: for flash messages
    ckeditor.init_app(app)
    bootstrap.init_app(app)
    gravatar.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Main application routes
    @app.route('/')
    def home():
        return render_template('index.html') # Renders 1. Main/templates/index.html

    @app.route('/about')
    def about():
        return render_template('about.html') # Renders 1. Main/templates/about.html

    @app.route('/contact')
    def contact():
        return render_template('contact.html') # Renders 1. Main/templates/contact.html

    # Register the blog blueprint
    # All routes from blog_bp will be prefixed with /blog_project
    app.register_blueprint(blog_bp, url_prefix='/blog_project')

    with app.app_context():
        db.create_all() # Create database tables for all models

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 