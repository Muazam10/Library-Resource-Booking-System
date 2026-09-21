from pydantic import BaseModel
from typing import Optional
import uuid
from app.models.resource import ResourceType

class ResourceCreate(BaseModel):
    name: str
    type: ResourceType
    location: Optional[str] = None
    capacity: Optional[int] = None

class ResourceOut(BaseModel):
    id: uuid.UUID
    name: str
    type: ResourceType
    location: Optional[str] = None
    capacity: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ResourceType] = None
    location: Optional[str] = None
    capacity: Optional[int] = None

