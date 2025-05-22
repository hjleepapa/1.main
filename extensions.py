from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5
# from flask_gravatar import Gravatar
from sqlalchemy.orm import DeclarativeBase

# Define a base for declarative models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
ckeditor = CKEditor()
bootstrap = Bootstrap5() # Instance for Bootstrap
# gravatar = Gravatar(
#     size=100,
#     rating='g',
#     default='retro',
#     force_default=False,
#     force_lower=False,
#     use_ssl=False,  # Consider setting to True in production if using HTTPS
#     base_url=None)