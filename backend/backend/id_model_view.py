from typing import ClassVar, TypeVar

from flask import jsonify, request
from flask.sansio.scaffold import Scaffold
from flask.views import MethodView

from backend.models import IdModel

DEFAULT_PER_PAGE = 12
MAX_PER_PAGE = 60


def api_response(errors: list[str] | None = None, **kwargs):
    response = {
        "success": errors is None or len(errors) == 0,
    }

    if errors:
        kwargs["errors"] = errors

    response.update(kwargs)

    return jsonify(response)


class ItemApi(MethodView):
    init_every_request = False

    def __init__(self, modelView: type["IdModelView"]):
        self.modelView = modelView

    def get(self, key):
        return self.modelView.read(key=key)

    def patch(self, key):
        return self.modelView.update(key=key)

    def delete(self, key):
        return self.modelView.delete(key=key)


class GroupApi(MethodView):
    init_every_request = False

    def __init__(self, modelView: type["IdModelView"]):
        self.modelView = modelView

    def get(self):
        return self.modelView.list()

    def post(self):
        return self.modelView.create()


T = TypeVar("T", bound=type[IdModel])


class IdModelView:
    model: ClassVar[T] = None
    name: ClassVar[str] = None

    required_create_params: ClassVar[list[str]] = []
    optional_create_params: ClassVar[list[str]] = []

    updatable_params: ClassVar[list[str]] = []

    item_key: ClassVar[str] = "<int:key>"

    @classmethod
    def filtered_params(
        cls,
        allowed_params: list[str],
        required: bool = False,
    ) -> tuple[dict | None, set[str]]:
        data = request.json

        if not isinstance(data, dict):
            return None, {
                "Top level of request object must be object",
            }

        errors = set()
        filtered = {}

        for key in allowed_params:
            if key in data:
                filtered[key] = data[key]
            elif required:
                errors.add(f"`{key}` is required")

        return filtered, errors

    @classmethod
    def list(cls):
        page = max(1, int(request.args.get("p", 1)))
        per_page = min(
            MAX_PER_PAGE, max(1, int(request.args.get("per_page", DEFAULT_PER_PAGE)))
        )

        page = cls.model.paginate(page, per_page)

        return api_response(page=page)

    @classmethod
    def validate_creation_params(cls, **kwargs) -> "list[str]":
        return []

    @classmethod
    def _post_create_hook(cls, new_instance: IdModel):
        pass

    @classmethod
    def _pre_create_hook(cls) -> "list[str]":
        return []

    @classmethod
    def create(cls):
        pre_create_errors = cls._pre_create_hook()

        if pre_create_errors:
            return api_response(errors=pre_create_errors)

        required_params, rerrors = cls.filtered_params(cls.required_create_params, True)
        optional_params, oerrors = cls.filtered_params(
            cls.optional_create_params, False
        )

        errors = list(rerrors | oerrors)

        if len(errors):
            return api_response(errors=errors)

        params = {**required_params, **optional_params}

        if errors := cls.validate_creation_params(**params):
            return api_response(errors=list(errors))

        new_instance = cls.model(**params).save()

        cls._post_create_hook(new_instance)

        return api_response(item=new_instance), 201

    @classmethod
    def get_by_key(cls, key):
        return cls.model.get_by_id(key)

    @classmethod
    def read(cls, key):
        if (item := cls.get_by_key(key)) is None:
            return api_response(errors=["Not found"]), 404

        return api_response(item=item)

    @classmethod
    def update(cls, key):
        if len(cls.updatable_params) == 0:
            return api_response(errors=["Not updatable"]), 405

        if (item := cls.get_by_key(key)) is None:
            return api_response(errors=["Not found"]), 404

        params, errors = cls.filtered_params(cls.updatable_params)

        if len(errors):
            return api_response(errors=list(errors))

        for key, value in params.items():
            setattr(item, key, value)

        item.save()

        return api_response(item=item)

    @classmethod
    def delete(cls, key):
        if (item := cls.get_by_key(key)) is None:
            return api_response(errors=["Not found"]), 404

        item.delete()

        return api_response()

    @classmethod
    def register_view(cls, app: Scaffold):
        if cls.model is None:
            raise Exception(f"{cls.__name__}.model must be defined")

        if cls.name is None:
            raise Exception(f"{cls.__name__}.name must be defined")

        items = ItemApi.as_view(f"{cls.name}-items", cls)
        group = GroupApi.as_view(f"{cls.name}-group", cls)

        app.add_url_rule(f"/{cls.name}/{cls.item_key}", view_func=items)
        app.add_url_rule(f"/{cls.name}/", view_func=group)
