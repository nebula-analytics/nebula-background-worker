import re

from utils import receives_config, ConfigMap

excluded_fields = ["_id"]

""" Map core fields to other names """


# mapped_fields = {"pnx_id": "_id"}

# core_fields = list(mapped_fields.get(key, key) for key in core_fields)


def convert_field_names(name: str, primo: ConfigMap):
    name = name.replace("@", "_")
    fixed = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    fixed = re.sub('([a-z0-9])([A-Z])', r'\1_\2', fixed).lower()
    mapped = primo.name_mapping.get(fixed, fixed)
    return mapped


@receives_config("primo")
def transform(input_data: dict, primo: ConfigMap) -> dict:
    output_data = {}
    for key, value in input_data.items():
        key = convert_field_names(key, primo)
        if key in primo.excluded_fields:
            continue
        output_data[key] = value

    output_data["_id"] = output_data.pop(primo.key_by)

    common_fields = list(primo.name_mapping.get(key, key) for key in primo.common_fields)

    core_data = {
        key: output_data[key] for key in common_fields
    }

    extra_data = {
        key: output_data[key] for key in output_data if key not in common_fields
    }

    core_data["extra_fields"] = extra_data

    return core_data
