from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, conint
from typing import List
from fastapi_sqlalchemy import db
from app.models.models import Reservation, Ride, User, ReservationStatus
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class ReservationCreate(BaseModel):
    ride_id: conint(gt=0)

class ReservationResponse(BaseModel):
    id: int
    passenger_id: int
    ride_id: int
    status: str

    class Config:
        orm_mode = True

@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def book_seat(reservation: ReservationCreate, token: str = Depends(oauth2_scheme)):
    """
    Book a seat on a ride by a passenger.
    """
    user_id = int(token)  # Placeholder, replace with actual decoding
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user or user.role.name != 'passenger':
        raise HTTPException(status_code=403, detail="Only passengers can book seats")
    ride = db.session.query(Ride).filter(Ride.id == reservation.ride_id, Ride.status == 'active').first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not available")
    if ride.seats_available < 1:
        raise HTTPException(status_code=400, detail="No seats available")
    existing_reservation = db.session.query(Reservation).filter(
        Reservation.passenger_id == user_id,
        Reservation.ride_id == reservation.ride_id
    ).first()
    if existing_reservation:
        raise HTTPException(status_code=400, detail="Already booked this ride")
    new_reservation = Reservation(
        passenger_id=user_id,
        ride_id=reservation.ride_id,
        status=ReservationStatus.pending
    )
    ride.seats_available -= 1
    db.session.add(new_reservation)
    db.session.commit()
    return new_reservation

@router.post("/confirm/{reservation_id}")
def confirm_reservation(reservation_id: int, token: str = Depends(oauth2_scheme)):
    """
    Confirm a reservation (simulate payment).
    """
    user_id = int(token)  # Placeholder, replace with actual decoding
    reservation = db.session.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.passenger_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=400, detail="Reservation not pending")
    # Simulate payment logic here
    reservation.status = ReservationStatus.confirmed
    db.session.commit()
    return {"msg": "Reservation confirmed and payment completed"}

@router.post("/cancel/{reservation_id}")
def cancel_reservation(reservation_id: int, token: str = Depends(oauth2_scheme)):
    """
    Cancel a reservation.
    """
    user_id = int(token)  # Placeholder, replace with actual decoding
    reservation = db.session.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.passenger_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if reservation.status == ReservationStatus.cancelled:
        raise HTTPException(status_code=400, detail="Reservation already cancelled")
    reservation.status = ReservationStatus.cancelled
    reservation.ride.seats_available += 1
    db.session.commit()
    return {"msg": "Reservation cancelled successfully"}
