from dataclasses import make_dataclass

from marshmallow import Schema, fields, post_load

from Models.BaseRecord import BaseRecord
from Models.PrimoIdentifier import PrimoIdentifier


class PrimoRecordSchema(Schema):
    class Meta:
        unknown = "include"

    title = fields.Str()
    creator = fields.List(fields.Str())
    subjects = fields.List(fields.Str(), data_key="subject")

    source_id = fields.Str(data_key="sourceId")
    lang = fields.Str(data_key="lang3")
    published = fields.Str(data_key="date")
    type = fields.Str(data_key="@TYPE")

    source_system = fields.Str(data_key="sourceSystem")
    source_record_id = fields.Str(data_key="sourcerecordid")

    identifiers = fields.List(fields.Nested(PrimoIdentifier), data_key="identifier")
    topics = fields.List(fields.Str(), data_key="topic")

    frbr_type = fields.Str(data_key="frbrType")
    context = fields.Str()
    institution = fields.Str()
    pnx_id = fields.Str(data_key="pnxId")

    @post_load
    def serial(self, data, **kwargs):
        keys = list(self.fields.keys())
        keys.append("extra_data")

        record_class = make_dataclass("PrimoRecord", keys, bases=(BaseRecord,))

        core_data = {
            key: data[key] for key in self.fields
        }
        extra_data = {
            key: data[key] for key in data if key not in core_data
        }

        core_data["extra_data"] = extra_data

        return record_class(**core_data)
