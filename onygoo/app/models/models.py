from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Enum
from app.extensions import db
import enum

class UserRole(enum.Enum):
    driver = "driver"
    passenger = "passenger"
    admin = "admin"

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship('Profile', uselist=False, back_populates='user')
    rides = relationship('Ride', back_populates='driver')
    reservations = relationship('Reservation', back_populates='passenger')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    full_name = Column(String(100))
    phone_number = Column(String(20))
    photo_url = Column(String(255))
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    user = relationship('User', back_populates='profile')

    def update_rating(self, new_rating):
        total_rating = self.rating * self.rating_count
        self.rating_count += 1
        self.rating = (total_rating + new_rating) / self.rating_count

class Ride(db.Model):
    __tablename__ = 'rides'
    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey('users.id'))
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    seats_available = Column(Integer, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    status = Column(String(50), default='active')  # active, cancelled, completed

    driver = relationship('User', back_populates='rides')
    reservations = relationship('Reservation', back_populates='ride')

class ReservationStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey('users.id'))
    ride_id = Column(Integer, ForeignKey('rides.id'))
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    passenger = relationship('User', back_populates='reservations')
    ride = relationship('Ride', back_populates='reservations')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey('reservations.id'))
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='completed')  # simulated payment status

    reservation = relationship('Reservation')

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship('User')

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship('User')
