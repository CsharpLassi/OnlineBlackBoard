from flask import Blueprint

bp = Blueprint("public", __name__)


@bp.route("/", methods=['GET', 'POST'])
def home():
    return 'Hello World'
