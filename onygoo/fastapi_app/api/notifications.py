from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
from typing import List, Optional
from fastapi_sqlalchemy import db
from app.models.models import Notification, User
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class NotificationCreate(BaseModel):
    title: constr(max_length=255)
    message: constr(max_length=1000)
    user_id: Optional[int]

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    user_id: Optional[int]
    created_at: str

    class Config:
        orm_mode = True

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, token: str = Depends(oauth2_scheme)):
    """
    Create a notification for a user or broadcast.
    """
    # Authentication and authorization logic here
    new_notification = Notification(
        title=notification.title,
        message=notification.message,
        user_id=notification.user_id
    )
    db.session.add(new_notification)
    db.session.commit()
    return new_notification

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(user_id: Optional[int] = None, token: str = Depends(oauth2_scheme)):
    """
    Get notifications for a user or all if no user_id provided.
    """
    query = db.session.query(Notification)
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    notifications = query.all()
    return notifications
