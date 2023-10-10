import os

import yaml
from pydantic import EmailStr, Field, create_model
from pydantic_settings import BaseSettings


class PathStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field):
        validator = getattr(cls, "_validator", None)
        if validator is None or not validator(value):
            raise ValueError(f"{value} is not a valid {cls.__name__} or doesn't exist.")
        return value


class FileStr(PathStr):
    _validator = staticmethod(os.path.isfile)


class DirStr(PathStr):
    _validator = staticmethod(os.path.isdir)


TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "EmailStr": EmailStr,
    "FileStr": FileStr,
    "DirStr": DirStr,
}


def load_yaml(filename: str) -> dict:
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def create_dynamic_settings(yaml_filename: str) -> BaseSettings:
    config = load_yaml(yaml_filename)
    fields = {}
    for name, value in config.items():
        field_info = value.get("field_info", {})
        field_type_str = value.get("type")
        field_type = TYPE_MAPPING.get(field_type_str)
        
        is_optional = value.get("optional", False)
        if is_optional:
            field_type = field_type | None
            field_info["default"] = field_info.get("default", None)

        fields[name] = (field_type, Field(**field_info))
    return create_model("DynamicSettings", __base__=BaseSettings, **fields)


DynamicSettings = create_dynamic_settings("env.yaml")
settings = DynamicSettings(_env_file=".env")
print(settings.dict())
print(settings.MEMBRANE_FRONTEND)
print(DynamicSettings.model_fields["MEMBRANE_FRONTEND"].description)
