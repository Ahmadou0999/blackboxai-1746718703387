from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import User, Ride
from functools import wraps

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role.name != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin dashboard showing stats and overview.
    """
    user_count = User.query.count()
    ride_count = Ride.query.count()
    return render_template('admin/dashboard.html', user_count=user_count, ride_count=ride_count)

@admin_bp.route('/users')
@admin_required
def manage_users():
    """
    List and manage users.
    """
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """
    Activate or deactivate a user.
    """
    user = User.query.get(user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
        flash('User status updated', 'success')
    else:
        flash('User not found', 'danger')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/rides')
@admin_required
def manage_rides():
    """
    List and manage rides.
    """
    rides = Ride.query.all()
    return render_template('admin/rides.html', rides=rides)

@admin_bp.route('/rides/<int:ride_id>/cancel', methods=['POST'])
@admin_required
def cancel_ride(ride_id):
    """
    Cancel a ride.
    """
    ride = Ride.query.get(ride_id)
    if ride:
        ride.status = 'cancelled'
        db.session.commit()
        flash('Ride cancelled', 'success')
    else:
        flash('Ride not found', 'danger')
    return redirect(url_for('admin.manage_rides'))
