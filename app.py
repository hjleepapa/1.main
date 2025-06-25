from flask import Flask, render_template, request # Added request
import os
from dotenv import load_dotenv
import hashlib
from extensions import db, login_manager, ckeditor, bootstrap, migrate # gravatar # Import migrate
from flask_login import current_user # Import current_user
import smtplib

# --- Global Helper Functions & Configuration ---
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

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
    # Centralized database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app, db) # Initialize Flask-Migrate

    # --- Configure Login Manager ---
    # This must be done after initializing the extensions and before registering blueprints that use it.
    login_manager.init_app(app)
    login_manager.login_view = 'blog.login' # Point to the blueprint's login route

    # The user_loader callback needs the User model.
    from blog_project.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # --- Register Blueprints ---
    # Import and register blueprints after all extensions are fully configured.
    # This prevents circular dependencies where blueprint code might need an initialized extension.
    from blog_project.main import blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog_project')

    from vapi_todo.vapi1_flask import vapi_flask_bp
    app.register_blueprint(vapi_flask_bp) # The url_prefix is already set in vapi1_flask.py

    # --- Main Application Routes ---
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/blog-tech-spec')
    def blog_tech_spec():
        """Renders the technical specification page for the blog project."""
        return render_template('blog_tech_spec.html')

    @app.route('/contact', methods=["GET", "POST"])
    def contact():
        msg_sent = False
        error_message = None
        if request.method == "POST":
            name = request.form.get("name")
            email_from = request.form.get("email")
            phone = request.form.get("phone")
            message_body = request.form.get("message")

            if not all([name, email_from, message_body]):
                error_message = "Please fill in all required fields (Name, Email, Message)."
                return render_template('contact.html', current_user=current_user, msg_sent=False, error=error_message)

            mail_server = os.environ.get('MAIL_SERVER')
            mail_port = int(os.environ.get('MAIL_PORT', 587))
            mail_username = os.environ.get('MAIL_USERNAME')
            mail_password = os.environ.get('MAIL_PASSWORD')
            mail_receiver = os.environ.get('MAIL_RECEIVER')

            if not all([mail_server, mail_username, mail_password, mail_receiver]):
                print("Email configuration is incomplete for main contact form.")
                error_message = "Message could not be sent due to a server configuration issue."
                return render_template('contact.html', current_user=current_user, msg_sent=False, error=error_message)

            email_subject = f"New Contact Form Submission from {name} (Main Site)"
            full_email_message = (
                f"Subject: {email_subject}\n\n"
                f"Name: {name}\nEmail: {email_from}\nPhone: {phone if phone else 'Not provided'}\n\nMessage:\n{message_body}\n"
            )

            try:
                with smtplib.SMTP(mail_server, mail_port) as server:
                    server.starttls()
                    server.login(mail_username, mail_password)
                    server.sendmail(mail_username, mail_receiver, full_email_message.encode('utf-8'))
                msg_sent = True
            except Exception as e:
                print(f"Error sending email from main contact form: {e}")
                error_message = "An unexpected error occurred. Please try again later."

        return render_template('contact.html', current_user=current_user, msg_sent=msg_sent, error=error_message)

    # --- Aircall Integration ---
    # Simple in-memory storage for call data (replace with database/Redis for production)
    # call_data_store = {}

    # def store_call_data(call_id, key, value):
    #     if call_id not in call_data_store:
    #         call_data_store[call_id] = {}
    #     call_data_store[call_id][key] = value

    # def retrieve_call_data(call_id, key):
    #     return call_data_store.get(call_id, {}).get(key)

    # def clear_call_data(call_id):
    #     if call_id in call_data_store:
    #         del call_data_store[call_id]

    # def fetch_customer_data_from_database(badge_number, pin_from_ivr):
    #     user = User.query.filter_by(badge=badge_number).first()
    #     if user and check_password_hash(user.pin, pin_from_ivr):
    #         return {
    #             "id": user.id, "name": user.name, "email": user.email,
    #             "badgeNumber": user.badge, "category": user.category,
    #             "company": user.company if user.company else "N/A"
    #         }
    #     return None

    # def send_insight_card_to_aircall(call_id, customer_data):
    #     import base64
    #     import requests
    #     aircall_api_id = os.environ.get("AIRCALL_API_ID")
    #     aircall_api_token = os.environ.get("AIRCALL_API_TOKEN")
    #     if not aircall_api_id or not aircall_api_token:
    #         print("Error: Aircall API ID or Token not configured.")
    #         return
    #     insight_card_payload = { "content": { "title": "Customer Information", "description": f"{customer_data.get('name', 'N/A')} - {customer_data.get('company', 'N/A')}", "fields": [ {"type": "text", "label": "Badge Number", "value": customer_data.get('badgeNumber', 'N/A')}, {"type": "text", "label": "Customer ID", "value": str(customer_data.get('id', 'N/A'))}, {"type": "text", "label": "Category", "value": customer_data.get('category', 'N/A')}, {"type": "text", "label": "Email", "value": customer_data.get('email', 'N/A')}, ] } }
    #     auth_string = f"{aircall_api_id}:{aircall_api_token}"
    #     headers = { "Authorization": "Basic " + base64.b64encode(auth_string.encode()).decode(), "Content-Type": "application/json" }
    #     url = f"https://api.aircall.io/v1/calls/{call_id}/insight_cards"
    #     try:
    #         response = requests.post(url, json=insight_card_payload, headers=headers, timeout=10)
    #         response.raise_for_status()
    #         print(f"Aircall Insight card created for call {call_id}: {response.json()}")
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error creating Aircall insight card for call {call_id}: {e}")

    # @app.route('/aircall/calls', methods=['POST'])
    # def handle_aircall_call():
    #     event_payload = request.json
    #     if not event_payload:
    #         return jsonify({"status": "error", "message": "Request must be JSON"}), 400
    #     event_type = event_payload.get("event")
    #     data = event_payload.get("data", {})
    #     call_id = data.get("id")
    #     print(f"Aircall Webhook: Event: {event_type}, Call ID: {call_id}")
    #     if event_type == 'call.created' and call_id:
    #         ivr_details = data.get("ivr", {})
    #         ivr_input = ivr_details.get("digits")
    #         ivr_step = ivr_details.get("step")
    #         if ivr_input is not None:
    #             if ivr_step == 1:
    #                 store_call_data(call_id, 'badge_number', ivr_input)
    #             elif ivr_step == 2:
    #                 store_call_data(call_id, 'pin', ivr_input)
    #                 badge_number = retrieve_call_data(call_id, 'badge_number')
    #                 pin_from_storage = retrieve_call_data(call_id, 'pin')
    #                 if badge_number and pin_from_storage:
    #                     customer_data = fetch_customer_data_from_database(badge_number, pin_from_storage)
    #                     if customer_data:
    #                         send_insight_card_to_aircall(call_id, customer_data)
    #                     clear_call_data(call_id)
    #     elif event_type == 'call.ended' and call_id:
    #         clear_call_data(call_id)
    #     return jsonify({"status": "webhook received"}), 200

    # --- Context Processors ---
    @app.context_processor
    def utility_processor():
        return dict(gravatar_url=generate_gravatar_url, user=current_user)

    return app

# Create the application instance for WSGI servers like Gunicorn to find.
app = create_app()

if __name__ == '__main__':
    # This is for local development only.
    app.run(debug=True)