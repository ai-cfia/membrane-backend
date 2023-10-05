import os

import yaml
from pydantic import EmailStr, Field, create_model
from pydantic_settings import BaseSettings


class FileStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field):
        if not os.path.exists(value):
            raise ValueError(f"File {value} doesn't exist.")
        return value


TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "EmailStr": EmailStr,
    "FileStr": FileStr,  # Add FileStr here
}


def load_yaml(filename: str) -> dict:
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def create_dynamic_settings(yaml_filename: str) -> BaseSettings:
    config = load_yaml(yaml_filename)
    fields = {}
    for name, value in config.items():
        field_info = value.get("field_info", {})
        field_type = TYPE_MAPPING.get(value.get("type"))
        fields[name] = (field_type, Field(**field_info))

    return create_model("DynamicSettings", __base__=BaseSettings, **fields)


DynamicSettings = create_dynamic_settings("env.yaml")
settings = DynamicSettings(_env_file=".env")
print(settings.dict())
