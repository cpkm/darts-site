from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_verification(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.verified:
            flash('Please verify your account!', 'warning')
            return redirect(url_for('auth.unverified_email'))
        return func(*args, **kwargs)
    return decorated_function


def check_role(roles):
    def check_role_decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.role in roles:
                flash('You do not have permission to view this page.', 'warning')
                return redirect(url_for('main.index'))
            return func(*args, **kwargs)
        return decorated_function
    return check_role_decorator