import datetime as dt
from typing import Union, Dict, Any
from pydantic import BaseModel, ValidationError as PydanticValidationError

# --- Common Schemas for Tool Calling ---

class ToolCallFunction(BaseModel):
    name: str
    arguments: Union[str, Dict[str, Any]]

class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction

class Message(BaseModel):
    toolCalls: list[ToolCall]

class ToolRequest(BaseModel):
    """A generic request model for any tool-calling service."""
    message: Message

# --- Common Response Schemas ---

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    completed: bool
    model_config = {'from_attributes': True}

class ReminderResponse(BaseModel):
    id: int
    reminder_text: str
    importance: str
    model_config = {'from_attributes': True}

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    event_from: dt.datetime
    event_to: dt.datetime
    model_config = {'from_attributes': True}