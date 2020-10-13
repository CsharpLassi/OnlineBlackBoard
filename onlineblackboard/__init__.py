from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    load_blueprints(app)

    return app


def load_blueprints(app: Flask):
    from .public.views import bp as bp_public
    app.register_blueprint(bp_public)
