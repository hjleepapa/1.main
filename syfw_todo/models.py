from extensions import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class SyfwTodo(db.Model):
    __tablename__ = 'todos_syfw'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID

class SyfwReminder(db.Model):
    __tablename__ = 'reminders_syfw'
    id = Column(Integer, primary_key=True, index=True)
    reminder_text = Column(String)
    importance = Column(String)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID

class SyfwCalendarEvent(db.Model):
    __tablename__ = 'calendar_events_syfw'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    event_from = Column(DateTime)
    event_to = Column(DateTime)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID 