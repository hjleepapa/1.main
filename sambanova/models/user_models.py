"""
User and Team Models for Sambanova
Database models for authentication and team collaboration
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from sambanova.mcps.local_servers.db_todo import Base

class UserRole(PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class TeamRole(PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users_sambanova"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    team_memberships = relationship("TeamMembership", back_populates="user")
    # created_todos = relationship("DBTodo", back_populates="creator")
    # assigned_todos = relationship("DBTodo", back_populates="assignee")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_team_roles(self):
        """Get all team roles for this user"""
        return {membership.team_id: membership.role for membership in self.team_memberships}

class Team(Base):
    __tablename__ = "teams_sambanova"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Team settings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    members = relationship("TeamMembership", back_populates="team")
    # todos = relationship("DBTodo", back_populates="team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
    
    def get_members(self):
        """Get all team members with their roles"""
        return [(membership.user, membership.role) for membership in self.members]
    
    def get_admins(self):
        """Get all team admins and owners"""
        return [membership.user for membership in self.members 
                if membership.role in [TeamRole.OWNER, TeamRole.ADMIN]]

class TeamMembership(Base):
    __tablename__ = "team_memberships_sambanova"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams_sambanova.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users_sambanova.id'), nullable=False)
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")
    
    def __repr__(self):
        return f"<TeamMembership(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"

# Update existing DBTodo model to support teams
# We'll need to modify the existing db_todo.py file
