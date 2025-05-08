from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from fastapi_sqlalchemy import db
from app.models.models import User, Profile
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class ProfileBase(BaseModel):
    full_name: Optional[constr(max_length=100)]
    phone_number: Optional[constr(max_length=20)]
    photo_url: Optional[str]

class ProfileResponse(ProfileBase):
    rating: Optional[float]
    rating_count: Optional[int]

    class Config:
        orm_mode = True

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(token: str = Depends(oauth2_scheme)):
    """
    Get the profile of the current logged-in user.
    """
    # Decode token to get user id (implementation depends on JWT setup)
    user_id = int(token)  # Placeholder, replace with actual decoding
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user or not user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user.profile

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(profile: ProfileBase, token: str = Depends(oauth2_scheme)):
    """
    Update the profile of the current logged-in user.
    """
    user_id = int(token)  # Placeholder, replace with actual decoding
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.profile:
        user.profile = Profile()
    if profile.full_name is not None:
        user.profile.full_name = profile.full_name
    if profile.phone_number is not None:
        user.profile.phone_number = profile.phone_number
    db.session.commit()
    return user.profile
