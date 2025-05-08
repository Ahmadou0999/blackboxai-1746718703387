from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import mail
from flask_mail import Message
import threading

notifications_bp = Blueprint('notifications', __name__)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

@notifications_bp.route('/send_email', methods=['POST'])
@jwt_required()
def send_email():
    """
    Send an email notification.
    Expects JSON with subject, recipients (list), body.
    """
    data = request.get_json()
    subject = data.get('subject')
    recipients = data.get('recipients')
    body = data.get('body')

    if not subject or not recipients or not body:
        return jsonify({'msg': 'Missing required fields'}), 400

    msg = Message(subject=subject, recipients=recipients, body=body)
    threading.Thread(target=send_async_email, args=(notifications_bp.app, msg)).start()
    return jsonify({'msg': 'Email sent'}), 200

@notifications_bp.route('/send_push', methods=['POST'])
@jwt_required()
def send_push_notification():
    """
    Send a push notification via Firebase.
    Expects JSON with title, message, tokens (list).
    """
    # This is a placeholder. Actual Firebase integration requires firebase_admin SDK and setup.
    data = request.get_json()
    title = data.get('title')
    message = data.get('message')
    tokens = data.get('tokens')

    if not title or not message or not tokens:
        return jsonify({'msg': 'Missing required fields'}), 400

    # TODO: Implement Firebase push notification sending here

    return jsonify({'msg': 'Push notification sent (simulated)'}), 200
