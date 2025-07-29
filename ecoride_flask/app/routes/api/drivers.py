from flask import (
    abort,
    current_app,
    Blueprint,
    request,
    render_template,
)
import logging
from app.db_store import driver_crud
from flask_login import login_required, current_user
from app.utils.custom_decorators import htmx_login_required, require_ownership

drivers_bp = Blueprint("drivers", __name__, url_prefix="/drivers")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@drivers_bp.route("/driver_data/<user_id>")
@htmx_login_required
@require_ownership("user_id")
def get_driver_data(user_id):
    user_id = request.view_args.get("user_id")
    owner = str(current_user.user_id) == str(user_id)

    driver_info = {}
    with current_app.db_manager.connection() as conn:
        driver_data = driver_crud.get_driver_data(conn, user_id)

        if driver_data:
            driver_id = driver_data["id"]
            driver_preferences = driver_crud.get_driver_preferences(conn, driver_id)
            driver_vehicles = driver_crud.get_driver_vehicles(conn, driver_id)

            driver_info = {
                "data": driver_data,
                "preferences": driver_preferences,
                "vehicles": driver_vehicles,
            }

    return render_template(
        "partials/driver_info.html",
        driver_data=driver_info,
        owner=owner,
    )


@drivers_bp.route("/edit_driver_preferences", methods=["GET", "POST"])
@htmx_login_required
@require_ownership("user_id")
def edit_driver_preferences():
    with current_app.db_manager.connection() as conn:
        driver_data = driver_crud.get_driver_data(conn, current_user.user_id)
        driver_id = driver_data["id"] if driver_data else None

        if request.method == "GET":
            prefs = driver_crud.get_driver_preferences(conn, driver_id)
            all_prefs = driver_crud.get_all_driver_preferences(conn)

            return render_template(
                "partials/driver_preferences_form.html",
                selected_prefs=prefs,
                all_prefs=all_prefs,
            )

        driver_data = driver_crud.get_driver_data(conn, current_user.user_id)
        driver_id = driver_data["id"] if driver_data else None

        new_prefs = request.form.getlist("preferences")
        print(f"New preferences from form: {new_prefs}")
        driver_crud.set_driver_preferences(conn, driver_id, new_prefs)

        # Re-fetch updated prefs for display
        updated_prefs = driver_crud.get_driver_preferences(conn, driver_id)
        print(f"Updated preferences: {updated_prefs}")
        return render_template(
            "partials/driver_preferences.html", preferences=updated_prefs, owner=True
        )


@drivers_bp.route("add_vehicle", methods=["GET", "POST"])
@htmx_login_required
@require_ownership("user_id")
def add_vehicle():
    if request.method == "GET":
        with current_app.db_manager.connection() as conn:
            brands = driver_crud.get_vehicle_brands(conn)
            energy_types = driver_crud.get_energy_types(conn)
        return render_template(
            "partials/add_vehicle_form.html", brands=brands, energy_types=energy_types
        )

    elif request.method == "POST":
        data = {
            "brand": request.form.get("brand_id"),
            "model": request.form.get("model"),
            "plate_number": request.form.get("plate_number"),
            "color": request.form.get("color"),
            "number_of_seats": request.form.get("number_of_seats"),
            "registration_date": request.form.get("registration_date"),
            "energy_type": request.form.get("energy_type_id"),
        }

        with current_app.db_manager.connection() as conn:
            driver_data = driver_crud.get_driver_data(conn, current_user.user_id)
            driver_id = driver_data["id"] if driver_data else None
            print(f"Driver ID: {driver_id}")

            driver_crud.add_vehicles(conn, driver_id, data)
            vehicles = driver_crud.get_driver_vehicles(conn, driver_id)
        return render_template(
            "partials/driver_vehicles.html", vehicles=vehicles, owner=True
        )


@drivers_bp.route("/remove_vehicle/<uuid:vehicle_id>", methods=["POST"])
@htmx_login_required
@require_ownership("user_id")
def remove_vehicle(vehicle_id):
    with current_app.db_manager.connection() as conn:
        driver_data = driver_crud.get_driver_data(conn, current_user.user_id)
        driver_id = driver_data["id"] if driver_data else None

        print(f"DRIVER : {driver_id}")
        vehicle = driver_crud.get_vehicle_by_id(conn, vehicle_id)
        if not vehicle or str(vehicle["driver_id"]) != str(driver_id):
            abort(403)
        driver_crud.remove_vehicles(conn, driver_id, [vehicle_id])
        vehicles = driver_crud.get_driver_vehicles(conn, driver_id)
    return render_template(
        "partials/driver_vehicles.html", vehicles=vehicles, owner=True
    )
