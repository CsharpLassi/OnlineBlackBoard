from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_assets import Environment

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
socket = SocketIO()
session = Session()
assets = Environment()

login.login_view = 'usable.login'
