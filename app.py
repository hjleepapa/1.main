from flask import Flask, render_template, request # Added request
import os
from dotenv import load_dotenv
import hashlib
from extensions import db, login_manager, ckeditor, bootstrap, migrate #, gravatar # Import migrate
import smtplib # Added for email sending
from flask_login import current_user # Import current_user
import requests # For sending requests to Aircall API
import base64   # For Basic Auth encoding
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

# --- Aircall Integration ---
# Simple in-memory storage for call data (replace with database/Redis for production)
call_data_store = {}

def store_call_data(call_id, key, value):
    if call_id not in call_data_store:
        call_data_store[call_id] = {}
    call_data_store[call_id][key] = value

def retrieve_call_data(call_id, key):
    return call_data_store.get(call_id, {}).get(key)

def clear_call_data(call_id):
    if call_id in call_data_store:
        del call_data_store[call_id]

def fetch_customer_data_from_database(badge_number, pin_from_ivr):
    # This function needs the app context to query the database
    # It will be available if called from within a request or if app_context is explicitly managed
    user = User.query.filter_by(badge=badge_number).first()
    if user and check_password_hash(user.pin, pin_from_ivr): # Assuming check_password_hash is accessible
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "badgeNumber": user.badge, # Match JS example field name
            "category": user.category,
            "company": user.company if user.company else "N/A"
        }
    return None

def send_insight_card_to_aircall(call_id, customer_data):
    aircall_api_id = os.environ.get("AIRCALL_API_ID")
    aircall_api_token = os.environ.get("AIRCALL_API_TOKEN")

    if not aircall_api_id or not aircall_api_token:
        print("Error: Aircall API ID or Token not configured in environment variables.")
        return

    insight_card_payload = {
        "content": {
            "title": "Customer Information",
            "description": f"{customer_data.get('name', 'N/A')} - {customer_data.get('company', 'N/A')}",
            "fields": [
                {"type": "text", "label": "Badge Number", "value": customer_data.get('badgeNumber', 'N/A')},
                {"type": "text", "label": "Customer ID", "value": str(customer_data.get('id', 'N/A'))},
                {"type": "text", "label": "Category", "value": customer_data.get('category', 'N/A')},
                {"type": "text", "label": "Email", "value": customer_data.get('email', 'N/A')},
            ]
        }
    }
    auth_string = f"{aircall_api_id}:{aircall_api_token}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_string.encode()).decode(),
        "Content-Type": "application/json"
    }
    url = f"https://api.aircall.io/v1/calls/{call_id}/insight_cards"

    try:
        response = requests.post(url, json=insight_card_payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Aircall Insight card created for call {call_id}: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating Aircall insight card for call {call_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Aircall API Response: {e.response.text}")
# --- End Aircall Integration ---

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
        from werkzeug.security import check_password_hash # Make sure it's available for fetch_customer_data
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
from flask import Blueprint, jsonify # jsonify was missing from this import block
from werkzeug.security import check_password_hash # For PIN verification

@app.route('/aircall/calls', methods=['POST'])
def handle_aircall_call():
    event_payload = request.json
    if not event_payload:
        print("Aircall Webhook: Received empty payload or not JSON")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    event_type = event_payload.get("event")
    data = event_payload.get("data", {})
    call_id = data.get("id")

    print(f"Aircall Webhook: Event: {event_type}, Call ID: {call_id}, Full Payload: {event_payload}")

    if event_type == 'call.created' and call_id:
        ivr_details = data.get("ivr", {})
        ivr_input = ivr_details.get("digits")
        # Aircall IVR step. Ensure to check Aircall docs if this is string or int. Assuming int.
        ivr_step = ivr_details.get("step") 

        if ivr_input is not None:
            print(f"Aircall IVR: Call ID: {call_id}, Step: {ivr_step}, Digits: {ivr_input}")
            if ivr_step == 1:  # Assuming step 1 is for badge
                store_call_data(call_id, 'badge_number', ivr_input)
                print(f"Aircall: Stored badge number for call {call_id}: {ivr_input}")
            elif ivr_step == 2:  # Assuming step 2 is for PIN
                store_call_data(call_id, 'pin', ivr_input)
                print(f"Aircall: Stored PIN for call {call_id}: {ivr_input}")

                badge_number = retrieve_call_data(call_id, 'badge_number')
                pin_from_storage = retrieve_call_data(call_id, 'pin')

                if badge_number and pin_from_storage:
                    print(f"Aircall: Attempting to fetch customer data for badge: {badge_number}")
                    customer_data = fetch_customer_data_from_database(badge_number, pin_from_storage)
                    if customer_data:
                        print(f"Aircall: Customer data found for call {call_id}: {customer_data}")
                        send_insight_card_to_aircall(call_id, customer_data)
                    else:
                        print(f"Aircall: No customer data found for badge {badge_number} with PIN for call {call_id}.")
                    clear_call_data(call_id) # Clean up after processing
                else:
                    print(f"Aircall: Missing badge or PIN for call {call_id} after IVR step 2.")
        else:
            print(f"Aircall IVR: No digits received for call {call_id}, step {ivr_step}.")

    elif event_type == 'call.answered' and call_id:
        print(f"Aircall: Call answered: {call_id}. Insight card should display if sent.")
        # Add logic here if you need to refresh or ensure card display on answer.

    elif event_type == 'call.ended' and call_id: # Good practice to clean up any stored data
        print(f"Aircall: Call ended: {call_id}. Clearing stored data.")
        clear_call_data(call_id)

    return jsonify({"status": "webhook received"}), 200

if __name__ == '__main__':
    # Create database tables if they don't exist
    # This should be done within the app context
    with app.app_context(): # Use the globally created app instance
        db.create_all()
    app.run(debug=True)