from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    url_for,
    make_response,
)
import logging
from app.db_store import user_crud
from flask_login import login_required, current_user
from app.utils.static_resolvers import static_id_resolver
from app.utils.custom_decorators import htmx_login_required, require_ownership

users_bp = Blueprint("users", __name__, url_prefix="/users")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@users_bp.route("/edit_roles", methods=["GET", "POST"])
@htmx_login_required
@require_ownership("user_id")
def edit_roles():
    with current_app.db_manager.connection() as conn:
        if request.method == "GET":
            all_roles = user_crud.get_roles_list(conn)
            current_roles = user_crud.get_user_roles(conn, current_user.user_id)

            return render_template(
                "partials/edit_roles_form.html",
                all_roles=all_roles,
                current_roles=current_roles,
            )

        elif request.method == "POST":
            new_roles = request.form.getlist("roles")

            print(f"New roles from form: {new_roles}")
            new_roles_ids = [
                role_id
                for role_id in new_roles
                if static_id_resolver("roles", role_id) is not None
            ]

            print(f"New roles IDs: {new_roles_ids}")

            worked = user_crud.set_user_roles(conn, current_user.user_id, new_roles_ids)

            print(f"Roles update worked: {worked}")

            response = make_response("", 204)
            response.headers["HX-Redirect"] = url_for(
                "pages.profile", user_id=current_user.user_id
            )
            return response


@users_bp.route("/get_account_credits")
@htmx_login_required
@require_ownership("user_id")
def get_account_credits():
    with current_app.db_manager.connection() as conn:
        credits = user_crud.get_user_credits(conn, current_user.user_id)
    return render_template("partials/credits_fragment.html", credits=credits)
