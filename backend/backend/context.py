from flask import g, session

from .models import User


def get_user() -> User | None:
    if "user" in g:
        return g.user

    if (user_id := session.get("user_id")) is None:
        return None

    if (user := User.get_by_id(user_id)) is None:
        clear_user()
        return None

    g.user = user
    return user


def set_user(user: User):
    session["user_id"] = user.id
    g.user = user


def clear_user():
    session.pop("user_id")

    g.user = None
