from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import User, Profile, Ride, Reservation
from werkzeug.utils import secure_filename
from app.forms.profile_forms import ProfileForm, ProfilePhotoForm
import os

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/me', methods=['GET', 'POST'])
@jwt_required()
def update_my_profile():
    """
    Get and update the profile of the current logged-in user using WTForms.
    Renders profile form on GET, processes form on POST.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.login'))

    form = ProfileForm(obj=user.profile)
    if form.validate_on_submit():
        if not user.profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            user.profile = profile
        user.profile.full_name = form.full_name.data
        user.profile.phone_number = form.phone_number.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profiles.update_my_profile'))

    return render_template('profiles/profile.html', form=form, profile=user.profile)

@profiles_bp.route('/me/photo', methods=['GET', 'POST'])
@jwt_required()
def upload_profile_photo():
    """
    Upload or update profile photo using WTForms.
    Accepts multipart/form-data with file field 'photo'.
    Saves file and updates photo_url in profile.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.login'))

    form = ProfilePhotoForm()
    if form.validate_on_submit():
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        upload_folder = 'static/uploads/profile_photos'
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        photo.save(filepath)

        if not user.profile:
            profile = Profile(user_id=user.id, photo_url=filepath)
            db.session.add(profile)
            user.profile = profile
        else:
            user.profile.photo_url = filepath

        db.session.commit()
        flash('Profile photo updated', 'success')
        return redirect(url_for('profiles.upload_profile_photo'))

    return render_template('profiles/upload_photo.html', form=form)

@profiles_bp.route('/<int:user_id>/rating', methods=['GET'])
def get_user_rating(user_id):
    """
    Get the rating and rating count of a user by user_id.
    """
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'msg': 'Profile not found'}), 404

    return jsonify({
        'rating': profile.rating,
        'rating_count': profile.rating_count
    }), 200

@profiles_bp.route('/me/rides', methods=['GET'])
@jwt_required()
def get_my_ride_history():
    """
    Get the ride history of the current logged-in user.
    Includes rides as driver and reservations as passenger.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    # Rides as driver
    rides = [{
        'id': ride.id,
        'origin': ride.origin,
        'destination': ride.destination,
        'departure_time': ride.departure_time.isoformat(),
        'seats_available': ride.seats_available,
        'status': ride.status
    } for ride in user.rides]

    # Reservations as passenger
    reservations = [{
        'id': res.id,
        'ride_id': res.ride.id,
        'origin': res.ride.origin,
        'destination': res.ride.destination,
        'departure_time': res.ride.departure_time.isoformat(),
        'status': res.status.value
    } for res in user.reservations]

    return jsonify({
        'rides_as_driver': rides,
        'reservations_as_passenger': reservations
    }), 200
