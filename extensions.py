from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5
# from flask_gravatar import Gravatar # No longer needed
from flask_migrate import Migrate # Import Migrate
from sqlalchemy.orm import DeclarativeBase

# Define a base for declarative models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
ckeditor = CKEditor()
bootstrap = Bootstrap5() # Instance for Bootstrap
migrate = Migrate() # Create a Migrate instance
