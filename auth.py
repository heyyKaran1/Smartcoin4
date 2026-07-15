import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')

class AuthManager:
    def __init__(self):
        self.users = {}
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@ccicoin.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        self.register_user(admin_email, admin_password, 'admin')

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def register_user(self, email, password, role='user'):
        if email in self.users:
            return None

        self.users[email] = {
            'email': email,
            'password': self.hash_password(password),
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        return self.users[email]

    def authenticate(self, email, password):
        user = self.users.get(email)
        if not user:
            return None

        if self.verify_password(password, user['password']):
            return self.generate_token(email, user['role'])
        return None

    def generate_token(self, email, role):
        payload = {
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

auth_manager = AuthManager()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        request.user = payload
        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        request.user = payload
        return f(*args, **kwargs)

    return decorated
