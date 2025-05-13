from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Database setup
db = SQLAlchemy()

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'