from pydantic import BaseModel, field_validator
from datetime import datetime
import uuid

class BookingCreate(BaseModel):
    resource_id: uuid.UUID
    start_time: datetime
    end_time: datetime

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, end_time, info):
        start_time = info.data.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return end_time

class BookingOut(BaseModel):
    id: uuid.UUID
    resource_id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        from_attributes = True