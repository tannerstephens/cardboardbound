from flask.json.provider import DefaultJSONProvider

from .models import IdModel, Page


class ModelJsonProvider(DefaultJSONProvider):
    def default(self, o: object):
        if isinstance(o, IdModel):
            return o.serialize()

        if isinstance(o, Page):
            return o.serialize()

        return super().default(o)
