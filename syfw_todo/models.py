from extensions import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class SyfwTodo(db.Model):
    __tablename__ = 'todos_syfw'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

class SyfwReminder(db.Model):
    __tablename__ = 'reminders_syfw'
    id = Column(Integer, primary_key=True, index=True)
    reminder_text = Column(String)
    importance = Column(String)

class SyfwCalendarEvent(db.Model):
    __tablename__ = 'calendar_events_syfw'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    event_from = Column(DateTime)
    event_to = Column(DateTime) 