import os

from marshmallow import Schema, fields


class PrimoIdentifier(Schema):
    idType = fields.Str()
    order = fields.Str(data_key="@id")
    id = fields.Str()

    @property
    def name(self):
        return os.path.basename(str(self.idType))