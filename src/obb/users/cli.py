import click
from flask import Blueprint

from ..ext import db

bp_cli = Blueprint("user", __name__)


@bp_cli.cli.command('create')
@click.argument('name')
@click.argument('email')
@click.argument('password')
def create_user(name, email, password):
    from .models import User
    admin = User(username=name,
                 email=email)
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()


@bp_cli.cli.command('create_admin')
@click.argument('name')
@click.argument('email')
@click.argument('password')
def create_admin(name, email, password):
    from .models import User
    admin = User(username=name,
                 email=email)
    admin.set_password(password)
    admin.is_admin = True

    db.session.add(admin)
    db.session.commit()
