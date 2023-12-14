from pydantic import BaseModel, create_model
from functools import wraps
from docstring_parser import parse


class Schema(BaseModel):
    @classmethod
    @property
    def custom_schema(cls):
        schema = cls.model_json_schema()
        docstring = parse(cls.__doc__ or "")
        parameters = {
            k: v for k, v in schema.items() if k not in ("title", "description")
        }
        for param in docstring.params:
            if (name := param.arg_name) in parameters["properties"] and (
                description := param.description
            ):
                if "description" not in parameters["properties"][name]:
                    parameters["properties"][name]["description"] = description

        parameters["required"] = sorted(
            k for k, v in parameters["properties"].items() if "default" not in v
        )

        if "description" not in schema:
            if docstring.short_description:
                schema["description"] = docstring.short_description
            else:
                schema["description"] = (
                    f"Correctly extracted `{cls.__name__}` with all "
                    f"the required parameters with correct types"
                )

        return {
            "name": schema["title"],
            "description": schema["description"],
            "parameters": parameters,
        }

    @classmethod
    def from_response(cls, chat, validation_context=None, strict: bool = None):
        message = chat.choices[0].message
        assert (
            message.function_call.name == cls.custom_schema["name"]
        ), "Function name does not match"
        return cls.model_validate_json(
            message.function_call.arguments, context=validation_context, strict=strict
        )


def convert_to_schema(cls) -> Schema:
    if not issubclass(cls, BaseModel):
        raise TypeError("Class must be subclass of pydantic.BaseModel")

    return wraps(cls, updated=())(create_model(cls.__name__, __base__=(cls, Schema)))
