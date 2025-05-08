from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import Reservation, Ride, User, Payment, ReservationStatus
from datetime import datetime
from app.forms.reservation_forms import ReservationForm

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/book', methods=['GET', 'POST'])
@jwt_required()
def book_seat():
    """
    Book a seat on a ride by a passenger using WTForms.
    Renders form on GET, processes form on POST.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role.name != 'passenger':
        flash('Only passengers can book seats', 'danger')
        return redirect(url_for('reservations.book_seat'))

    form = ReservationForm()
    if form.validate_on_submit():
        ride_id = form.ride_id.data
        ride = Ride.query.get(ride_id)
        if not ride or ride.status != 'active':
            flash('Ride not available', 'danger')
            return redirect(url_for('reservations.book_seat'))

        if ride.seats_available < 1:
            flash('No seats available', 'danger')
            return redirect(url_for('reservations.book_seat'))

        # Check if already booked
        existing_reservation = Reservation.query.filter_by(passenger_id=user_id, ride_id=ride_id).first()
        if existing_reservation:
            flash('Already booked this ride', 'warning')
            return redirect(url_for('reservations.book_seat'))

        reservation = Reservation(
            passenger_id=user_id,
            ride_id=ride_id,
            status=ReservationStatus.pending
        )
        db.session.add(reservation)
        ride.seats_available -= 1
        db.session.commit()
        flash('Seat booked, pending confirmation', 'success')
        return redirect(url_for('reservations.book_seat'))

    return render_template('reservations/book_seat.html', form=form)

from flask import request, jsonify, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.models import Reservation, Payment, ReservationStatus
from app.blueprints.reservations import reservations_bp

@reservations_bp.route('/confirm/<int:reservation_id>', methods=['POST'])
@jwt_required()
def confirm_reservation(reservation_id):
    """
    Confirm a reservation (simulate payment).
    """
    user_id = get_jwt_identity()
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        flash('Reservation not found', 'danger')
        return redirect(url_for('reservations.book_seat'))

    if reservation.passenger_id != user_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('reservations.book_seat'))

    if reservation.status != ReservationStatus.pending:
        flash('Reservation not pending', 'warning')
        return redirect(url_for('reservations.book_seat'))

    # Simulate payment
    payment = Payment(
        reservation_id=reservation.id,
        amount=reservation.ride.price_per_seat,
        status='completed'
    )
    db.session.add(payment)
    reservation.status = ReservationStatus.confirmed
    db.session.commit()
    flash('Reservation confirmed and payment completed', 'success')
    return redirect(url_for('reservations.book_seat'))

@reservations_bp.route('/cancel/<int:reservation_id>', methods=['POST'])
@jwt_required()
def cancel_reservation(reservation_id):
    """
    Cancel a reservation.
    """
    user_id = get_jwt_identity()
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        flash('Reservation not found', 'danger')
        return redirect(url_for('reservations.book_seat'))

    if reservation.passenger_id != user_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('reservations.book_seat'))

    if reservation.status == ReservationStatus.cancelled:
        flash('Reservation already cancelled', 'warning')
        return redirect(url_for('reservations.book_seat'))

    reservation.status = ReservationStatus.cancelled
    reservation.ride.seats_available += 1
    db.session.commit()
    flash('Reservation cancelled successfully', 'success')
    return redirect(url_for('reservations.book_seat'))
