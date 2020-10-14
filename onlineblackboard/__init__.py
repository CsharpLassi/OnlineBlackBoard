from typing import Optional, TypeVar

from flask import Flask
from .config import Config

C = TypeVar('C', bound=Config)


def create_app(conf: Optional[C] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(conf)

    load_ext(app)
    load_blueprints(app)
    load_cli(app)
    register_shellcontext(app)

    return app


def load_ext(app: Flask):
    from .ext import (
        db, migrate, login, socket)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    socket.init_app(app)


def load_blueprints(app: Flask):
    from .public.views import bp as bp_public
    app.register_blueprint(bp_public)

    from .blackboard.views import bp as bp_blackboard
    app.register_blueprint(bp_blackboard)


def load_cli(app: Flask):
    from .users.cli import bp_cli as bp_user
    app.register_blueprint(bp_user)


def register_shellcontext(app: Flask):
    from .ext import db
    from .users.models import User

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": User}

    app.shell_context_processor(shell_context)
