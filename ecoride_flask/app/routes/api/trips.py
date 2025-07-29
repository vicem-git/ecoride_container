from app.utils import htmx_login_required
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
)
import logging
from app.db_store import driver_crud, trips_crud
from datetime import datetime
from flask_login import login_required, current_user
from app.utils.static_resolvers import static_name_resolver
from app.utils.custom_decorators import require_ownership

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@trips_bp.route("/create_trip")
@login_required
def create_trip():
    return render_template("pages/create_trip.html", page_wrap="create_trip")


@trips_bp.route("/query_trips")
def query_trips():
    form = request.form
    start_date = form.get("start_date") or datetime.now().isoformat()

    print(f"Form data: {form}")

    with current_app.db_manager.connection() as conn:
        results = trips_crud.search_trips(
            conn,
            start_city=form.get("start_city"),
            end_city=form.get("end_city"),
            passenger_nr=form.get("passenger_nr"),
            start_date=form.get("start_date"),
        )

    return render_template(
        "partials/trip_results.html", page_wrap="query_trips", trips=results
    )


@trips_bp.route("/view_trip/<trip_id>")
@htmx_login_required
def view_trip():
    trip_id = request.view_args.get("trip_id")
    return render_template("partials/trip_detail.html", trip_id=trip_id)


@trips_bp.route("/passenger-trips/<status>")
@htmx_login_required
@require_ownership("user_id")
def passenger_trips_by_status(status):
    status = request.view_args.get("status")
    user_id = current_user.user_id

    try:
        status_id = static_name_resolver("trip_status", status)
    except Exception:
        return "Invalid status", 400

    with current_app.db_manager.connection() as conn:
        trips = trips_crud.get_passenger_trips(conn, user_id, status_id)

    return render_template("/partials/profile_trip_item.html", trips=trips or [])


@trips_bp.route("/driver-trips/<status>")
@htmx_login_required
@require_ownership("user_id")
def driver_trips_by_status(status):
    status = request.view_args.get("status")
    user_id = current_user.user_id

    try:
        status_id = static_name_resolver("trip_status", status)
    except Exception:
        return "Invalid status", 400

    requested_user_id = request.args.get("for_user", user_id)
    if requested_user_id != str(user_id):
        return "Forbidden", 403

    with current_app.db_manager.connection() as conn:
        driver_id = driver_crud.get_driver_data(conn, user_id)

        trips = trips_crud.get_driver_trips(conn, driver_id, status)

    return render_template("/partials/profile_trip_item.html", trips=trips or [])
