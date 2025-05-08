from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from app.extensions import db, jwt, mail
from app.models.models import User, EmailVerificationToken, PasswordResetToken
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from app.forms.auth_forms import RegistrationForm, LoginForm, RequestPasswordResetForm, ResetPasswordForm
import uuid

auth_bp = Blueprint('auth', __name__)

# Serializer for generating tokens
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
    except Exception:
        return False
    return email

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user (driver or passenger) using WTForms.
    Renders registration form on GET, processes form on POST.
    Sends email verification link.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        role = form.role.data

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate email verification token
        token = generate_token(email)
        verification_url = f"{request.host_url}auth/verify_email/{token}"

        # TODO: Send email with verification_url
        flash('User registered. Please verify your email.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    """
    Verify user's email using token.
    """
    email = confirm_token(token)
    if not email:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.register'))

    user.is_email_verified = True
    db.session.commit()
    flash('Email verified successfully', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login with email and password using WTForms.
    Renders login form on GET, processes form on POST.
    Returns JWT access token if successful.
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid credentials', 'danger')
            return render_template('auth/login.html', form=form)

        if not user.is_email_verified:
            flash('Email not verified', 'warning')
            return render_template('auth/login.html', form=form)

        access_token = create_access_token(identity=user.id)
        # For web, you might want to set the token in a cookie or session
        flash('Login successful', 'success')
        return redirect(url_for('profiles.get_my_profile'))
    return render_template('auth/login.html', form=form)

@auth_bp.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    """
    Request password reset by email using WTForms.
    Renders form on GET, processes on POST.
    Sends a reset token via email.
    """
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found', 'danger')
            return render_template('auth/request_password_reset.html', form=form)

        # Generate reset token
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.session.add(reset_token)
        db.session.commit()

        reset_url = f"{request.host_url}auth/reset_password/{token}"
        # TODO: Send email with reset_url
        flash('Password reset link sent to your email', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/request_password_reset.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password using token with WTForms.
    Renders form on GET, processes on POST.
    """
    form = ResetPasswordForm()
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.request_password_reset'))

    if form.validate_on_submit():
        new_password = form.password.data
        user = User.query.get(reset_token.user_id)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.register'))

        user.set_password(new_password)
        db.session.delete(reset_token)
        db.session.commit()
        flash('Password reset successful', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
