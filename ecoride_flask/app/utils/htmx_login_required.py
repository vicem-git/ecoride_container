from functools import wraps
from flask import current_app, redirect, url_for, request, make_response
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
