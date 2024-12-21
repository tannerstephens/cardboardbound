from flask import Blueprint, jsonify, request

from .context import clear_user, get_user, set_user
from .models import Invite, Submission, User

api = Blueprint("api", __name__, url_prefix="/api")

PER_PAGE = 20

from backend.context import get_user


def authenticated(func):
    def wrapper(*args, **kwargs):
        if get_user() is None:
            return "", 401

        return func(*args, **kwargs)

    return wrapper


def api_response(error_message: str | None = None, **kwargs):
    response = {
        "success": error_message is None,
    }

    if error_message:
        kwargs["error_message"] = error_message

    response.update(kwargs)

    return jsonify(response)


@api.route("/submissions", methods=["GET"])
@authenticated
def list_submissions():
    page = max(1, int(request.args.get("p", 1)))

    page = Submission.paginate(page)

    return api_response(page=page)


@api.route("/submissions", methods=["POST"])
def create_submission():
    data = request.json

    if not isinstance(data, dict):
        return api_response(False)

    if (title := data.get("title")) is None:
        return api_response(False, error="title is required")

    description = data.get("description")

    new_submission = Submission(title, description).save()

    return api_response(item=new_submission)


@api.route("/users", methods=["POST"])
def register():
    data = request.json

    if not isinstance(data, dict):
        return api_response(error_message="root level should be object")

    if (username := data.get("username")) is None:
        return api_response(error_message="username is required")

    if (password := data.get("password")) is None:
        return api_response(error_message="password is required")

    if (invite_code := data.get("invite")) is None:
        return api_response(error_message="invite is required")

    if not User.validate_password(password):
        return api_response(error_message="password must be at least 8 characters")

    if User.get_by_username(username):
        return api_response(error_message="username already taken")

    if (invite := Invite.get_active_invite(invite_code)) is None:
        return api_response(error_message="invite is not valid")

    new_user = User(username, password).save()

    invite.used = True
    invite.save()

    return api_response(item=new_user)


@api.route("/session", methods=["POST"])
def login():
    data = request.json

    if not isinstance(data, dict):
        return api_response(error_message="root level should be object")

    if (username := data.get("username")) is None:
        return api_response(error_message="username is required")

    if (password := data.get("password")) is None:
        return api_response(error_message="password is required")

    if (user := User.get_by_username(username)) is None or not user.check_password(password):
        return api_response(error_message="username or password incorrect")

    set_user(user)

    return api_response(item=user)


@api.route("/session", methods=["GET"])
def me():
    return api_response(item=get_user())


@api.route("/session", methods=["DELETE"])
def logout():
    clear_user()
    return api_response()
