from flask import Blueprint, render_template, flash, redirect, url_for, request

from ..tools import admin_required
from ..ext import db

from .models import User

bp = Blueprint('users.admin', __name__, url_prefix='/users/admin')


@bp.route('/', methods=['GET', "POST"])
@admin_required
def home():
    users = User.query.all()
    return render_template('users/admin/home.html', users=users)


@bp.route('/<int:user_id>', methods=['GET', "POST"])
@admin_required
def detail(user_id: int):
    from .forms_admin import EditForm, ChangePasswordForm, DeleteForm

    user = User.query.get(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('users.admin.home'))

    update_counter = 0

    edit_form = EditForm()
    if request.args.get('edit') == 'user' and edit_form.validate_on_submit():
        new_email = edit_form.email.data
        new_username = edit_form.username.data

        if new_email != user.email:
            if User.query.filter_by(email=new_email).count() == 0:
                user.email = new_email
                update_counter += 1
            else:
                flash('E-Mail already exist')

        if new_username != user.username:
            if User.query.filter_by(username=new_username).count() == 0:
                user.username = new_username
                update_counter += 1
            else:
                flash('Username already exist')

    change_password_form = ChangePasswordForm()
    if request.args.get('edit') == 'password' and \
            change_password_form.validate_on_submit():
        new_password = change_password_form.password.data
        user.set_password(new_password)
        update_counter += 1

    delete_form = DeleteForm()
    if request.args.get('edit') == 'delete' and delete_form.validate_on_submit():
        if user.username == delete_form.username.data:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('users.admin.home'))

    change_password_form.password.data = None
    change_password_form.password2.data = None

    if update_counter > 0:
        db.session.commit()

    edit_form.username.data = user.username
    edit_form.email.data = user.email

    return render_template('users/admin/detail.html', user=user,
                           edit_form=edit_form,
                           change_password_form=change_password_form,
                           delete_form=delete_form)
