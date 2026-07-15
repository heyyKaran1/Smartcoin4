from flask_wtf.csrf import CSRFProtect, generate_csrf
from functools import wraps
from flask import request, jsonify
import secrets

csrf = CSRFProtect()

def init_csrf(app):
    """Initialize CSRF protection"""
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit
    csrf.init_app(app)

    @app.after_request
    def set_csrf_cookie(response):
        """Set CSRF token in cookie for frontend"""
        if request.endpoint and not request.endpoint.startswith('static'):
            token = generate_csrf()
            response.set_cookie('csrf_token', token,
                              secure=False,  # Set to True in production with HTTPS
                              httponly=False,  # Must be False so JS can read it
                              samesite='Lax')
        return response

    return csrf

def csrf_exempt(f):
    """Decorator to exempt routes from CSRF"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    decorated_function._csrf_exempt = True
    return decorated_function

def get_csrf_token():
    """Generate CSRF token for frontend"""
    return generate_csrf()
