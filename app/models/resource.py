import uuid
import enum
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base

class ResourceType(str, enum.Enum):
    seat = "seat"
    room = "room"
    equipment = "equipment"

class Resource(Base):
    __tablename__ = "resource"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(Enum(ResourceType), nullable=False)
    location = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())