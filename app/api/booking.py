from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.models.booking import Booking
from app.models.resource import Resource
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.core.security import get_current_user
from typing import List
import uuid
from app.models.booking import BookingStatus

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

@router.get("/me", response_model=List[BookingOut])
def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to view this booking")

    return booking


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    booking.status = BookingStatus.cancelled
    db.commit()
    return {"detail": "Booking cancelled successfully"}

