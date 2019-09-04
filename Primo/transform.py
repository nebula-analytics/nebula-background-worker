import re

core_fields = ['title', 'identifier', 'lang3', '_type', 'sourcerecordid', 'subject', 'frbr_type', 'date', 'topic',
               'creator', 'source_system', 'pnx_id', 'source_id', "context"]

excluded_fields = ["_id"]

""" Map core fields to other names """
mapped_fields = {"pnx_id": "_id"}

core_fields = list(mapped_fields.get(key, key) for key in core_fields)


def convert_field_names(name: str):
    name = name.replace("@", "_")
    fixed = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    fixed = re.sub('([a-z0-9])([A-Z])', r'\1_\2', fixed).lower()
    mapped = mapped_fields.get(fixed, fixed)
    return mapped


def transform(input_data: dict) -> dict:
    output_data = {}
    for key, value in input_data.items():
        output_data[convert_field_names(key)] = value

    core_data = {
        key: output_data[key] for key in core_fields
    }

    extra_data = {
        key: output_data[key] for key in output_data if key not in core_fields
    }

    core_data["extra_fields"] = extra_data

    return core_data
