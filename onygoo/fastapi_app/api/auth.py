from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime, timedelta
from fastapi_sqlalchemy import db
from app.models.models import User, Role
from app.extensions import jwt
from jose import JWTError, jwt as jose_jwt
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jose_jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    """
    Register a new user with email, password, and role.
    """
    existing_user = db.session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    role_obj = db.session.query(Role).filter(Role.name == user.role).first()
    if not role_obj:
        raise HTTPException(status_code=400, detail="Invalid role")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, password_hash=hashed_password, role=role_obj)
    db.session.add(new_user)
    db.session.commit()
    # TODO: Send email verification asynchronously
    return {"msg": "User registered. Please verify your email."}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login with email and password. Returns JWT access token.
    """
    user = db.session.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Additional endpoints for email verification, password reset can be added here with proper models and logic
