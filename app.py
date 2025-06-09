from flask import Flask, render_template, request # Added request
import os
from dotenv import load_dotenv
import hashlib
from extensions import db, login_manager, ckeditor, bootstrap, migrate #, gravatar # Import migrate
import smtplib # Added for email sending
from flask_login import current_user # Import current_user
from blog_project.main import blog_bp # Changed from relative to absolute
from blog_project.models import User # Changed from relative to absolute, Needed for user_loader

from vapi_todo.vapi1_flask import vapi_flask_bp # Adjust path if necessary




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
    migrate.init_app(app, db) # Initialize Flask-Migrate
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

    # vapi_flask_todo blueprints:
    app.register_blueprint(vapi_flask_bp) # The url_prefix is already set in vapi1_flask.py

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

@app.route('/contact', methods=["GET", "POST"]) # Allow POST requests
def contact():
    msg_sent = False
    error_message = None
    if request.method == "POST":
        name = request.form.get("name")
        email_from = request.form.get("email")
        phone = request.form.get("phone")
        message_body = request.form.get("message")

        if not all([name, email_from, message_body]): # Phone might be optional
            error_message = "Please fill in all required fields (Name, Email, Message)."
            return render_template('contact.html', current_user=current_user, msg_sent=False, error=error_message)

        # Email configuration (ensure these are in your .env file)
        mail_server = os.environ.get('MAIL_SERVER')
        mail_port = int(os.environ.get('MAIL_PORT', 587))
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        mail_receiver = os.environ.get('MAIL_RECEIVER')

        if not all([mail_server, mail_username, mail_password, mail_receiver]):
            print("Email configuration is incomplete for main contact form. Please check environment variables.")
            error_message = "Message could not be sent due to a server configuration issue."
            # Log this error for admin review
            return render_template('contact.html', current_user=current_user, msg_sent=False, error=error_message)

        email_subject = f"New Contact Form Submission from {name} (Main Site)"
        full_email_message = (
            f"Subject: {email_subject}\n\n"
            f"You have received a new message from your main website contact form.\n\n"
            f"Name: {name}\n"
            f"Email: {email_from}\n"
            f"Phone: {phone if phone else 'Not provided'}\n\n"
            f"Message:\n{message_body}\n"
        )

        try:
            with smtplib.SMTP(mail_server, mail_port) as server:
                server.starttls()
                server.login(mail_username, mail_password)
                server.sendmail(mail_username, mail_receiver, full_email_message.encode('utf-8'))
            msg_sent = True
        except Exception as e:
            print(f"Error sending email from main contact form: {e}") # Log this
            error_message = "An unexpected error occurred while sending your message. Please try again later."

    # For GET request or after POST processing
    return render_template('contact.html', current_user=current_user, msg_sent=msg_sent, error=error_message)

# Aircall webhook route
from flask import Blueprint
@app.route('/aircall/calls', methods=['POST'])
def handle_aircall_call():
  return '', 200

if __name__ == '__main__':
    # Create database tables if they don't exist
    # This should be done within the app context
    with app.app_context(): # Use the globally created app instance
        db.create_all()
    app.run(debug=True)