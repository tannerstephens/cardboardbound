import click
from flask import Blueprint

from .models import User

commands = Blueprint("commands", __name__, cli_group=None)


@commands.cli.command("make-user")
@click.argument("username")
@click.argument("password")
def make_user(username, password):
    return User(username, password).save()


@commands.cli.command("make-admin")
@click.argument("username")
def make_admin(username):
    user = User.get_by_username(username)

    if user:
        user.admin = True
        user.save()
