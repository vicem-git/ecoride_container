from functools import wraps
from flask import abort, redirect, url_for, request, make_response
from flask_login import current_user


def htmx_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.headers.get("HX-Request"):
                response = make_response("", 401)
                response.headers["HX-Redirect"] = url_for("auth.login")
                return response
            else:
                return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def require_ownership(param="user_id"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get(param)
            if not user_id or str(user_id) != str(current_user.user_id):
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator
