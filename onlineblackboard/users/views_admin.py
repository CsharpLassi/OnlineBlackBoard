from flask import Blueprint, render_template

from .models import User

bp = Blueprint('users.admin', __name__, url_prefix='/users/admin')


@bp.route('/', methods=['GET', "POST"])
def home():
    users = User.query.all()
    return render_template('users/admin/home.html', users=users)
