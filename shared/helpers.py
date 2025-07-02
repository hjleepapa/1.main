from flask import request, abort
from pydantic import ValidationError as PydanticValidationError
from .schemas import ToolRequest, ToolCall

def get_validated_tool_call(expected_function_name: str) -> ToolCall:
    """
    Validates the incoming JSON request against the ToolRequest schema
    and returns the specific tool call matching the expected function name.
    """
    json_data = request.get_json()
    if not json_data:
        abort(400, description="Invalid JSON payload.")

    try:
        # Validate the entire request structure
        tool_req = ToolRequest(**json_data)
    except PydanticValidationError as e:
        abort(400, description=f"Invalid request format: {e.errors()}")

    # Find the specific tool call we are looking for
    for tool_call in tool_req.message.toolCalls:
        if tool_call.function.name == expected_function_name:
            # If arguments are a string, parse them into a dict
            if isinstance(tool_call.function.arguments, str):
                tool_call.function.arguments = request.json_loads(tool_call.function.arguments)
            return tool_call

    abort(400, description=f"Tool call with function name '{expected_function_name}' not found.")