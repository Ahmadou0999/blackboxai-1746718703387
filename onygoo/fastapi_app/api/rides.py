from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, constr, conint, confloat
from typing import List, Optional
from datetime import datetime
from fastapi_sqlalchemy import db
from app.models.models import Ride, User
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class RideBase(BaseModel):
    origin: constr(max_length=255)
    destination: constr(max_length=255)
    departure_time: datetime
    seats_available: conint(gt=0)
    price_per_seat: confloat(ge=0)

class RideCreate(RideBase):
    pass

class RideResponse(RideBase):
    id: int
    driver_id: int
    status: str

    class Config:
        orm_mode = True

@router.post("/", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
def propose_ride(ride: RideCreate, token: str = Depends(oauth2_scheme)):
    """
    Propose a new ride by a driver.
    """
    user_id = int(token)  # Placeholder, replace with actual decoding
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user or user.role.name != 'driver':
        raise HTTPException(status_code=403, detail="Only drivers can propose rides")
    new_ride = Ride(
        driver_id=user.id,
        origin=ride.origin,
        destination=ride.destination,
        departure_time=ride.departure_time,
        seats_available=ride.seats_available,
        price_per_seat=ride.price_per_seat,
        status='active'
    )
    db.session.add(new_ride)
    db.session.commit()
    return new_ride

@router.get("/", response_model=List[RideResponse])
def search_rides(
    origin: Optional[str] = Query(None, max_length=255),
    destination: Optional[str] = Query(None, max_length=255),
    date: Optional[datetime] = None
):
    """
    Search for rides by origin, destination, and optional date.
    """
    query = db.session.query(Ride).filter(Ride.status == 'active')
    if origin:
        query = query.filter(Ride.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Ride.destination.ilike(f"%{destination}%"))
    if date:
        query = query.filter(Ride.departure_time >= date)
    rides = query.all()
    return rides
