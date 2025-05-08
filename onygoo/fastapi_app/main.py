from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db
from fastapi_app.api import auth, profiles, rides, reservations, notifications

app = FastAPI(
    title="Onygoo FastAPI Backend",
    description="API backend for Onygoo carpooling mobile app",
    version="1.0.0"
)

# Add CORS middleware for Flutter app consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add DB session middleware
app.add_middleware(DBSessionMiddleware, db_url="mysql+pymysql://user:password@localhost/onygoo")

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
app.include_router(rides.router, prefix="/rides", tags=["rides"])
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
