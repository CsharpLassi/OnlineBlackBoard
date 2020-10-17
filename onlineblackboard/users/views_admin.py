from flask import Blueprint, render_template, flash, redirect, url_for

from .models import User
from ..tools import admin_required

bp = Blueprint('users.admin', __name__, url_prefix='/users/admin')


@bp.route('/', methods=['GET', "POST"])
@admin_required
def home():
    users = User.query.all()
    return render_template('users/admin/home.html', users=users)


@bp.route('/<int:user_id>', methods=['GET', "POST"])
@admin_required
def detail(user_id: int):
    user = User.query.get(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('users.admin.home'))

    return render_template('users/admin/detail.html', user=user)
