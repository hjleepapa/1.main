import json
from flask import request, abort
from pydantic import ValidationError as PydanticValidationError
from .schemas import syfwRequest, ToolCall

def _get_validated_tool_call(expected_function_name: str) -> ToolCall:
    json_data = request.get_json()
    if not json_data:
        abort(400, description="Invalid JSON payload. Request body must be JSON.")
    try:
        syfw_req = syfwRequest(**json_data)
    except PydanticValidationError as e:
        abort(400, description=f"Invalid request format: {e.errors()}")
    for tool_call in syfw_req.message.toolCalls:
        if tool_call.function.name == expected_function_name:
            if isinstance(tool_call.function.arguments, str):
                try:
                    tool_call.function.arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    abort(400, description=f"Tool call '{expected_function_name}' arguments are not valid JSON.")
            return tool_call
    abort(400, description=f"Invalid Request: Tool call '{expected_function_name}' not found.") 