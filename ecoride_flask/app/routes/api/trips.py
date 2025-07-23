from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
)
import logging
from app.db_store import trips_crud
from datetime import datetime


trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@trips_bp.route("/<trip_id>")
def trip_details(trip_id):
    return render_template("partials/trip_details.html", trip_id=trip_id)


@trips_bp.route("/create_trip")
def create_trip():
    return render_template("pages/create_trip.html", page_wrap="create_trip")


@trips_bp.route("/query_trips", methods=["GET", "POST"])
def query_trips():
    form = request.form
    start_date = form.get("start_date") or datetime.now().isoformat()

    print(f"Form data: {form}")

    with current_app.db_manager.connection() as conn:
        results = trips_crud.search_trip_summaries(
            conn,
            start_city=form.get("start_city"),
            end_city=form.get("end_city"),
            max_price=form.get("max_price"),
            start_date=form.get("start_date"),
        )

    return render_template(
        "partials/trip_results.html", page_wrap="query_trips", trips=results
    )
