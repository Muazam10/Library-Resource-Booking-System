from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.models.booking import Booking
from app.models.resource import Resource
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.core.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resource = db.query(Resource).filter(
        Resource.id == booking_in.resource_id,
        Resource.is_active == True,
    ).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    new_booking = Booking(
        resource_id=booking_in.resource_id,
        user_id=current_user.id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
    )
    db.add(new_booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This resource is already booked for the requested time slot",
        )
    db.refresh(new_booking)
    return new_booking

