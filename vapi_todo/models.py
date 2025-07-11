# models.py
from extensions import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class VapiTodo(db.Model):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID

class VapiReminder(db.Model):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True, index=True)
    reminder_text = Column(String)
    importance = Column(String)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID

class VapiCalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    event_from = Column(DateTime)
    event_to = Column(DateTime)
    google_calendar_event_id = Column(String, nullable=True)  # Google Calendar event ID
