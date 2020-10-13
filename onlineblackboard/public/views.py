from flask import Blueprint, render_template

bp = Blueprint("public", __name__)


@bp.route("/", methods=['GET', 'POST'])
def home():
    return render_template('public/home.html')
