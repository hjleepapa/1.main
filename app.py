from flask import Flask, render_template
import os
from dotenv import load_dotenv
import hashlib
from extensions import db, login_manager, ckeditor, bootstrap #, gravatar # This is fine
from flask_login import current_user # Import current_user
from blog_project.main import blog_bp # Changed from relative to absolute
from blog_project.models import User # Changed from relative to absolute, Needed for user_loader

def generate_gravatar_url(email, size=80, default_image='mp', rating='g'):
    """
    Generates a Gravatar URL for a given email address.

    :param email: The email address (string).
    :param size: Size of the avatar in pixels (integer).
    :param default_image: Default image type (e.g., 'mp', 'identicon', '404').
    :param rating: Rating of the avatar (e.g., 'g', 'pg', 'r', 'x').
    :return: The Gravatar URL (string).
    """
    if email is None: # Handle None email gracefully
        email = ''
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    # Always use HTTPS for Gravatar URLs
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default_image}&r={rating}"

load_dotenv() # It's common to load dotenv at the module level or early in create_app

def create_app():
    app = Flask(__name__)

    @app.context_processor
    def utility_processor():
        return dict(gravatar_url=generate_gravatar_url, user=current_user)

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
    # gravatar.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # return db.session.get(User, int(user_id))
        # This function is called to reload the user object from the user ID stored in the session.
        # Flask-Login ensures it runs within an appropriate context to access db.
        return User.query.get(int(user_id))
    
    # Register the blog blueprint
    # All routes from blog_bp will be prefixed with /blog_project
    app.register_blueprint(blog_bp, url_prefix='/blog_project')

    with app.app_context():
        db.create_all() # Create database tables for all models

    return app

# Create the Flask app instance
# This is the main entry point for the application.
# It will be used by Gunicorn or any other WSGI server.
# This is the main application file.
# It initializes the Flask app and registers the main routes.
# This is the main application file.
    
# Create the Flask app instance globally so Gunicorn can find it.
# This also makes the 'app' instance available for any module-level decorators
# like @app.route (if used outside blueprints) or for the __main__ block.
app = create_app()

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


# @login_manager.user_loader
# def load_user(user_id):
#     # This function is called to reload the user object from the user ID stored in the session.
#     # Flask-Login ensures it runs within an appropriate context to access db.
#     return User.query.get(int(user_id))

if __name__ == '__main__':
    # Create database tables if they don't exist
    # This should be done within the app context
    with app.app_context(): # Use the globally created app instance
        db.create_all()
    app.run(debug=True)