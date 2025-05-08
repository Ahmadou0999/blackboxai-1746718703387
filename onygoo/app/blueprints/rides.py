from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import Ride, User
from datetime import datetime
from app.forms.ride_forms import RideForm

rides_bp = Blueprint('rides', __name__)

@rides_bp.route('/propose', methods=['GET', 'POST'])
@jwt_required()
def propose_ride():
    """
    Propose a new ride by a driver using WTForms.
    Renders form on GET, processes form on POST.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role.name != 'driver':
        flash('Only drivers can propose rides', 'danger')
        return redirect(url_for('rides.propose_ride'))

    form = RideForm()
    if form.validate_on_submit():
        ride = Ride(
            driver_id=user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data,
            seats_available=form.seats_available.data,
            price_per_seat=form.price_per_seat.data,
            status='active'
        )
        db.session.add(ride)
        db.session.commit()
        flash('Ride proposed successfully', 'success')
        return redirect(url_for('rides.propose_ride'))

    return render_template('rides/propose_ride.html', form=form)

@rides_bp.route('/search', methods=['GET'])
def search_rides():
    """
    Search for rides by origin, destination, and optional date.
    Query parameters: origin, destination, date (ISO format, optional)
    """
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date_str = request.args.get('date')

    if not origin or not destination:
        return jsonify({'msg': 'Origin and destination are required'}), 400

    query = Ride.query.filter(
        Ride.origin.ilike(f'%{origin}%'),
        Ride.destination.ilike(f'%{destination}%'),
        Ride.status == 'active'
    )

    if date_str:
        try:
            date = datetime.fromisoformat(date_str).date()
            query = query.filter(db.func.date(Ride.departure_time) == date)
        except ValueError:
            return jsonify({'msg': 'Invalid date format'}), 400

    rides = query.all()
    results = []
    for ride in rides:
        results.append({
            'id': ride.id,
            'driver_id': ride.driver_id,
            'origin': ride.origin,
            'destination': ride.destination,
            'departure_time': ride.departure_time.isoformat(),
            'seats_available': ride.seats_available,
            'price_per_seat': ride.price_per_seat,
            'status': ride.status
        })

    return jsonify(results), 200

@rides_bp.route('/<int:ride_id>', methods=['PUT'])
@jwt_required()
def modify_ride(ride_id):
    """
    Modify an existing ride by the driver.
    Expects JSON with any of origin, destination, departure_time, seats_available, price_per_seat, status.
    """
    user_id = get_jwt_identity()
    ride = Ride.query.get(ride_id)
    if not ride:
        return jsonify({'msg': 'Ride not found'}), 404

    if ride.driver_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.get_json()
    if 'origin' in data:
        ride.origin = data['origin']
    if 'destination' in data:
        ride.destination = data['destination']
    if 'departure_time' in data:
        try:
            ride.departure_time = datetime.fromisoformat(data['departure_time'])
        except ValueError:
            return jsonify({'msg': 'Invalid departure_time format'}), 400
    if 'seats_available' in data:
        ride.seats_available = data['seats_available']
    if 'price_per_seat' in data:
        ride.price_per_seat = data['price_per_seat']
    if 'status' in data:
        ride.status = data['status']

    db.session.commit()
    return jsonify({'msg': 'Ride updated successfully'}), 200

@rides_bp.route('/<int:ride_id>', methods=['DELETE'])
@jwt_required()
def cancel_ride(ride_id):
    """
    Cancel a ride by the driver.
    """
    user_id = get_jwt_identity()
    ride = Ride.query.get(ride_id)
    if not ride:
        return jsonify({'msg': 'Ride not found'}), 404

    if ride.driver_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    ride.status = 'cancelled'
    db.session.commit()
    return jsonify({'msg': 'Ride cancelled successfully'}), 200
