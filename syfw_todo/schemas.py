import datetime as dt
from typing import Union, Dict, Any
from pydantic import BaseModel, ValidationError as PydanticValidationError

class ToolCallFunction(BaseModel):
    name: str
    arguments: Union[str, Dict[str, Any]]

class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction

class Message(BaseModel):
    toolCalls: list[ToolCall]

class syfwRequest(BaseModel):
    message: Message

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    completed: bool
    class Config:
        from_attributes = True

class ReminderResponse(BaseModel):
    id: int
    reminder_text: str
    importance: str
    class Config:
        from_attributes = True

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    event_from: dt.datetime
    event_to: dt.datetime
    class Config:
        from_attributes = True 