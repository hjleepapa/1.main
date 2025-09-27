from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
import os
from pydantic import BaseModel
from enum import StrEnum
import pandas as pd
try:
    from google_calendar import get_calendar_service
except ImportError:
    # Fallback for when running as MCP server
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from google_calendar import get_calendar_service

# ----------------------------
# SQLAlchemy Models
# ----------------------------

class Base(DeclarativeBase):
     pass


class DBTodo(Base):
    __tablename__ = "todos_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    priority: Mapped[str] = mapped_column(String, nullable=False, server_default=text("medium"))
    due_date: Mapped[datetime] = mapped_column(nullable=True)
    google_calendar_event_id: Mapped[str] = mapped_column(String, nullable=True)


class DBReminder(Base):
    __tablename__ = "reminders_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    reminder_text: Mapped[str] = mapped_column(String, nullable=False)
    importance: Mapped[str] = mapped_column(String, nullable=False, server_default=text("medium"))
    reminder_date: Mapped[datetime] = mapped_column(nullable=True)
    google_calendar_event_id: Mapped[str] = mapped_column(String, nullable=True)


class DBCalendarEvent(Base):
    __tablename__ = "calendar_events_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"), onupdate=datetime.now)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    event_from: Mapped[datetime] = mapped_column(nullable=False)
    event_to: Mapped[datetime] = mapped_column(nullable=False)
    google_calendar_event_id: Mapped[str] = mapped_column(String, nullable=True)


class DBCallRecording(Base):
    __tablename__ = "call_recordings_sambanova"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    call_sid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    from_number: Mapped[str] = mapped_column(String, nullable=True)
    to_number: Mapped[str] = mapped_column(String, nullable=True)
    recording_path: Mapped[str] = mapped_column(String, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(nullable=True)
    transcription: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'completed'"))  # completed, failed, processing 

# ----------------------------
# Pydantic Models
# ----------------------------

class TodoPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Todo(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    title: str
    description: str
    completed: bool
    priority: TodoPriority
    due_date: datetime
    google_calendar_event_id: str


class ReminderImportance(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Reminder(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    reminder_text: str
    importance: ReminderImportance
    reminder_date: datetime
    google_calendar_event_id: str


class CalendarEvent(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    title: str
    description: str
    event_from: datetime
    event_to: datetime
    google_calendar_event_id: str


class CallRecording(BaseModel):
    id: UUID
    created_at: datetime
    call_sid: str
    from_number: str
    to_number: str
    recording_path: str
    duration_seconds: int
    file_size_bytes: int
    transcription: str
    status: str

# ----------------------------
# DB Session
# ----------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(url=os.getenv("DB_URI"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
