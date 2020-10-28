from typing import Optional, TypeVar

from flask import Flask
from .config import Config

C = TypeVar("C", bound=Config)


def create_app(conf: Optional[C] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(conf)

    load_ext(app)
    load_blueprints(app)
    load_cli(app)
    register_shellcontext(app)

    create_default(app)

    register_cron(app)

    return app


def load_ext(app: Flask):
    from .ext import session, db, migrate, login, socket, assets

    session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    socket.init_app(app, manage_session=False)
    assets.init_app(app)


def load_blueprints(app: Flask):
    from .public.views import bp as bp_public

    app.register_blueprint(bp_public)

    from .blackboard.views import bp as bp_blackboard

    app.register_blueprint(bp_blackboard)

    from .users.views import bp as bp_users
    from .users.views_admin import bp as bp_users_admin

    app.register_blueprint(bp_users)
    app.register_blueprint(bp_users_admin)

    # Filters
    from .filters import bp as bp_filters

    app.register_blueprint(bp_filters)


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


def create_default(app: Flask):
    import os

    path = app.config["BLACKBOARD_DATA_PATH"]
    if os.path.exists(path) and os.path.isdir(path):
        return
    os.mkdir(path)


def register_cron(app: Flask):
    from .blackboard.cron import bp as blackboard_cron

    app.register_blueprint(blackboard_cron)
