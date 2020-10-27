from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user

from ..ext import db

bp = Blueprint("public", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    return render_template("public/home.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    from ..users.forms import LoginForm
    from ..users.models import User

    if current_user.is_authenticated:
        return redirect(url_for("public.home"))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for("public.login"))
        login_user(user, remember=login_form.remember_me.data)
        return redirect(url_for("public.login"))

    return render_template("public/login.html", login_form=login_form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    from ..users.forms import RegistrationForm
    from ..users.models import User

    if current_user.is_authenticated:
        return redirect(url_for("public_home"))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(
            username=register_form.username.data, email=register_form.email.data
        )
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!", "success")
        return redirect(url_for("public.login"))

    return render_template(
        "public/register.html", title="Register", register_form=register_form
    )
