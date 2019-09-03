import re

core_fields = ['title', 'identifier', 'lang3', '_type', 'sourcerecordid', 'subject', 'frbr_type', 'date', 'topic',
               'creator', 'source_system', 'pnx_id', 'source_id', "context"]

excluded_fields = ["_id"]

""" Map core fields to other names """
mapped_fields = {"pnx_id": "_id"}


def convert_field_names(name: str):
    name = name.replace("@", "_")
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def transform(input_data: dict) -> dict:
    output_data = {}
    for key, value in input_data.items():
        new_field_name = convert_field_names(key)
        if new_field_name in mapped_fields:
            new_field_name = mapped_fields[new_field_name]
        output_data[new_field_name] = value

    core_data = {
        key: output_data[mapped_fields.get(key, key)] for key in core_fields
    }

    extra_data = {
        key: output_data[key] for key in output_data if key not in core_fields
    }

    core_data["extra_fields"] = extra_data

    return core_data
