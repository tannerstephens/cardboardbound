from flask import Blueprint, request

from .context import clear_user, get_user, set_user
from .id_model_view import IdModelView, api_response
from .models import Invite, Submission, User

api = Blueprint("api", __name__, url_prefix="/api")

MAX_PER_PAGE = 100
MIN_PER_PAGE = 10
DEFAULT_PER_PAGE = 20

from backend.context import get_user


def authenticated(func):
    def wrapper(*args, **kwargs):
        if get_user() is None:
            return api_response(errors=["Unauthenticated"]), 401

        return func(*args, **kwargs)

    return wrapper


def admin_only(func):
    @authenticated
    def wrapper(*args, **kwargs):
        if not get_user().admin:
            return api_response(errors=["Unauthorized"]), 403

        return func(*args, **kwargs)

    return wrapper


class SubmissionView(IdModelView):
    model = Submission
    name = "submissions"

    required_create_params = ["title"]
    optional_create_params = ["description"]

    updatable_params = ["title", "description"]

    @classmethod
    @authenticated
    def list(cls):
        return super().list()

    @classmethod
    @authenticated
    def read(cls, key):
        return super().read(key)

    @classmethod
    @authenticated
    def update(cls, key):
        return super().update(key)

    @classmethod
    @authenticated
    def delete(cls, key):
        return super().delete(key)


SubmissionView.register_view(api)


class UserView(IdModelView):
    model: type[User] = User
    name = "users"

    required_create_params = ["username", "password"]

    updatable_params = ["password"]

    item_key = "<key>"

    @classmethod
    def get_by_key(cls, key):
        return cls.model.get_by_username(key)

    @classmethod
    def validate_creation_params(cls, **kwargs):
        errors = []

        if not User.validate_password(kwargs["password"]):
            errors.append("Password must be at least 8 characters")

        if User.get_by_username(kwargs["username"]) is not None:
            errors.append("Username already in use")

        return errors

    @classmethod
    def _pre_create_hook(cls):
        if User.empty():
            return []

        invite_params, errors = cls.filtered_params(["invite"], True)

        if errors:
            return list(errors)

        if Invite.get_active_invite(invite_params["invite"]) is None:
            return ["Invalid invite"]

    @classmethod
    def _post_create_hook(cls, new: User):
        if User.empty():
            new.admin = True

        invite_params = cls.filtered_params(["invite"], True)

        invite = Invite.get_active_invite(invite_params["invite"])

        invite.used = True

        invite.save()

    @classmethod
    def current_key_is_user_or_admin(cls, key):
        return (user := get_user()) and (user.username == key or user.admin)

    @classmethod
    @admin_only
    def list(cls):
        return super().list()

    @classmethod
    @authenticated
    def update(cls, key):
        if not cls.current_key_is_user_or_admin(key):
            return api_response(["Unauthorized"]), 401

        return super().update(key)

    @classmethod
    @authenticated
    def delete(cls, key):
        if not cls.current_key_is_user_or_admin(key):
            return api_response(["Unauthorized"]), 401

        return super().delete(key)


UserView.register_view(api)


@api.route("/session", methods=["POST"])
def login():
    data = request.json

    if not isinstance(data, dict):
        return api_response(errors=["root level should be object"])

    if (username := data.get("username")) is None:
        return api_response(errors=["Username is required"])

    if (password := data.get("password")) is None:
        return api_response(errors=["Password is required"])

    if (user := User.get_by_username(username)) is None or not user.check_password(password):
        return api_response(errors=["Username or password incorrect"])

    set_user(user)

    return api_response(item=user)


@api.route("/session", methods=["GET"])
def me():
    return api_response(item=get_user())


@api.route("/session", methods=["DELETE"])
def logout():
    clear_user()
    return api_response()


class InviteView(IdModelView):
    model = Invite

    optional_create_params = ["expiration"]

    @classmethod
    @admin_only
    def create(cls):
        return super().create()

    @classmethod
    @admin_only
    def list(cls):
        return super().list()

    @classmethod
    @admin_only
    def read(cls, key):
        return super().read(key)

    @classmethod
    @admin_only
    def update(cls, key):
        return super().update(key)

    @classmethod
    @admin_only
    def delete(cls, key):
        return super().delete(key)
