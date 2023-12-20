from pydantic import BaseModel, ValidationError
from typing import (
    Optional,
    Callable,
    Type,
)
import openai
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
)
import json
from functools import wraps

from schema import Schema, convert_to_schema


def handle_response_model(*, response_model: Type[BaseModel], kwargs):
    new_kwargs = kwargs.copy()
    if response_model is not None:
        if not issubclass(response_model, Schema):
            response_model = convert_to_schema(response_model)

    new_kwargs["functions"] = [response_model.custom_schema]
    new_kwargs["function_call"] = {"name": response_model.custom_schema["name"]}
    return response_model, new_kwargs


def process_response(
    response,
    *,
    response_model: Type[BaseModel],
    stream: bool,
    validation_context: dict = None,
    strict: bool = None,
):
    model = response_model.from_response(response, validation_context, strict=strict)
    return model


def dump_message(message: ChatCompletionMessage) -> ChatCompletionMessageParam:
    return_value: ChatCompletionMessageParam = {
        "role": message.role,
        "content": message.content or "",
    }
    if message.tool_calls is not None:
        return_value["content"] += json.dumps(message.model_dump()["tool_calls"])
    if message.function_call is not None:
        return_value["content"] += json.dumps(message.model_dump()["function_call"])
    return return_value


def retry(
    func,
    response_model,
    validation_context,
    args,
    kwargs,
    max_retries,
    strict: Optional[bool] = None,
):
    retries = 0
    while retries <= max_retries:
        try:
            response = func(*args, **kwargs)
            stream = kwargs.get("stream", False)
            return process_response(
                response,
                response_model=response_model,
                stream=stream,
                validation_context=validation_context,
                strict=strict,
            )
        except (ValidationError, json.JSONDecodeError) as e:
            kwargs["messages"].append(dump_message(response.choices[0].message))
            kwargs["messages"].append(
                {
                    "role": "user",
                    "content": f"Recall the function correctly, exceptions found\n{e}",
                }
            )
            retries += 1
            if retries > max_retries:
                print(f"Max retries reach, exception: {e}")
                raise e


def modified_chat_completion(func: Callable) -> Callable:
    @wraps(func)
    def new_chat_completion(
        response_model=None, validation_context=None, max_retries=1, *args, **kwargs
    ):
        response_model, new_kwargs = handle_response_model(
            response_model=response_model, kwargs=kwargs
        )
        response = retry(
            func=func,
            response_model=response_model,
            validation_context=validation_context,
            max_retries=max_retries,
            args=args,
            kwargs=new_kwargs,
        )
        return response

    wrapper_function = new_chat_completion
    return wrapper_function


def modify_chat_completion(client: openai.OpenAI):
    client.chat.completions.create = modified_chat_completion(
        client.chat.completions.create
    )
