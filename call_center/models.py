"""
Call Center Models
"""

from datetime import datetime
from enum import Enum
from extensions import db

class AgentState(str, Enum):
    """Agent availability states"""
    LOGGED_OUT = "logged_out"
    LOGGED_IN = "logged_in"
    READY = "ready"
    NOT_READY = "not_ready"
    ON_CALL = "on_call"
    WRAP_UP = "wrap_up"

class CallState(str, Enum):
    """Call states"""
    IDLE = "idle"
    RINGING = "ringing"
    CONNECTED = "connected"
    HELD = "held"
    TRANSFERRING = "transferring"
    ENDED = "ended"

class Agent(db.Model):
    """Call Center Agent Model"""
    __tablename__ = 'cc_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    sip_extension = db.Column(db.String(50), unique=True)
    sip_username = db.Column(db.String(100))
    sip_password = db.Column(db.String(100))
    sip_domain = db.Column(db.String(100))
    state = db.Column(db.String(20), default=AgentState.LOGGED_OUT.value)
    state_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    calls = db.relationship('Call', backref='agent', lazy=True, cascade='all, delete-orphan')

class Call(db.Model):
    """Call Record Model"""
    __tablename__ = 'cc_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.String(100), unique=True, nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('cc_agents.id'))
    caller_number = db.Column(db.String(50))
    caller_name = db.Column(db.String(100))
    called_number = db.Column(db.String(50))
    customer_id = db.Column(db.String(100))
    customer_data = db.Column(db.JSON)  # Store customer info for popup
    state = db.Column(db.String(20), default=CallState.IDLE.value)
    direction = db.Column(db.String(10))  # inbound/outbound
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    disposition = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'call_id': self.call_id,
            'caller_number': self.caller_number,
            'caller_name': self.caller_name,
            'called_number': self.called_number,
            'customer_id': self.customer_id,
            'customer_data': self.customer_data,
            'state': self.state,
            'direction': self.direction,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration': self.duration
        }

class AgentActivity(db.Model):
    """Agent Activity Log"""
    __tablename__ = 'cc_agent_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('cc_agents.id'))
    activity_type = db.Column(db.String(50))  # login, logout, state_change, call_start, call_end
    from_state = db.Column(db.String(20))
    to_state = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(db.JSON)

