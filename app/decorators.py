from flask import session, redirect, url_for, flash
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('api.login'))
        return f(*args, **kwargs)
    return decorated_function



def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Please log in to acces this page.', 'error')
                return redirect(url_for('api.login'))
            if session.get('role') != role:
                flash('You dont have permission to access this page', 'error')
                return redirect(url_for('api.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
