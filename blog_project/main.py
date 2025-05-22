from datetime import date
from flask import Blueprint, abort, render_template, redirect, url_for, flash, request, jsonify
# Import extensions from the parent directory's extensions.py
from extensions import db, login_manager, ckeditor, bootstrap #, gravatar
from flask_login import login_user, current_user, logout_user
# Import models from the local models.py
from .models import BlogPost, User, Comment
# Import forms from the local forms.py
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists in this directory
# It's often better to have one .env file at the project root (1. Main/)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)

blog_bp = Blueprint('blog', __name__,
                    template_folder='templates',  # Will look for templates in blog_project/templates/
                    static_folder='static',       # Will look for static files in blog_project/static/
                    static_url_path='/blog_project/static') # URL for these static files

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        # Also check if user is authenticated
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Register new users into the User database
@blog_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('blog.login')) # Prefix with blueprint name

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        hashed_pin = generate_password_hash(
            form.pin.data,
            method='pbkdf2:sha256',  # Using the same strong hashing method
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            badge=form.badge.data,
            pin=hashed_pin
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("blog.get_all_posts")) # Prefix with blueprint name
    return render_template("register.html", form=form, current_user=current_user)


@blog_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('blog.login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('blog.login'))
        else:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('blog.get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@blog_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('blog.get_all_posts'))


# This will be the root of the blog, e.g., /blog_project/
@blog_bp.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("indexb.html", all_posts=posts, current_user=current_user)
    

# Add a POST method to be able to post comments
@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("blog.login", next=request.url))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('blog.show_post', post_id=post_id)) # Redirect to clear form
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


# Use a decorator so only an admin user can create new posts
@blog_bp.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("blog.get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


# Use a decorator so only an admin user can edit a post
@blog_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only # Ensure admin_only decorator is applied
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        # author=post.author, # For pre-filling, WTForms handles this if 'obj' is passed or data is set
        # For CreatePostForm, it doesn't have an author field to pre-fill directly
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("blog.show_post", post_id=post.id))
    # Pass post object to template if needed for display, and ensure form is pre-filled
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user, post=post)


# Use a decorator so only an admin user can delete a post
@blog_bp.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('blog.get_all_posts'))


# These will be /blog_project/about and /blog_project/contact
@blog_bp.route("/about")
def about():
    return render_template("aboutb.html", current_user=current_user)


@blog_bp.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contactb.html", current_user=current_user)


# API for Badge and PIN Authentication
@blog_bp.route("/api/authenticate_badge_pin", methods=["POST"])
def authenticate_badge_pin():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    badge = data.get("badge")
    pin = data.get("pin")

    if not badge or not pin:
        return jsonify({"status": "error", "message": "Missing badge or pin"}), 400

    # Find user by badge
    result = db.session.execute(db.select(User).where(User.badge == badge))
    user = result.scalar()

    if not user:
        return jsonify({"status": "error", "message": "Badge not found"}), 404

    # Check the PIN
    if check_password_hash(user.pin, pin):
        # Authentication successful
        # You might want to generate a token here for more robust API authentication
        return jsonify({
            "status": "success",
            "message": "Authentication successful",
            "user_id": user.id,
            "name": user.name
        }), 200
    else:
        return jsonify({"status": "error", "message": "Invalid PIN"}), 401
