from flask import (
    abort,
    current_app,
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    make_response,
)
import logging
from app.db_store import user_crud, driver_crud
from flask_login import login_user, logout_user, login_required, current_user
from app.utils.static_resolvers import static_name_resolver, static_id_resolver
from app.utils.htmx_login_required import htmx_login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@user_bp.route("/edit_roles", methods=["GET", "POST"])
@htmx_login_required
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


@user_bp.route("/get_account_credits")
@login_required
def get_account_credits():
    with current_app.db_manager.connection() as conn:
        credits = user_crud.get_user_credits(conn, current_user.user_id)
    return render_template("partials/credits_fragment.html", credits=credits)


@user_bp.route("/driver_data/<user_id>")
@login_required
def get_driver_data(user_id):
    with current_app.db_manager.connection() as conn:
        driver_data = driver_crud.get_driver_data(conn, user_id)
        if driver_data is None:
            return {"error": "Driver data not found"}, 404

        PREF_LABELS = {
            "smoking_allowed": "Fumeur autorisé",
            "non_smoking": "Non-fumeur",
            "pets_allowed": "Animaux acceptés",
            "no_pets_allowed": "Pas d'animaux",
            "music_allowed": "Musique autorisée",
            "no_music_allowed": "Pas de musique",
            "air_conditioning": "Climatisation",
            "no_air_conditioning": "Pas de climatisation",
        }

        prefs = driver_crud.get_driver_preferences(conn, str(driver_data[0]))
        vehicles = driver_crud.get_driver_vehicles(conn, user_id)
        return render_template(
            "partials/driver_info.html",
            driver_data=driver_data,
            prefs=prefs,
            labels=PREF_LABELS,
            vehicles=vehicles,
        )


@user_bp.route("/edit_driver_preferences", methods=["GET", "POST"])
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


@user_bp.route("add_vehicle", methods=["GET", "POST"])
@htmx_login_required
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


@user_bp.route("/remove_vehicle/<uuid:vehicle_id>", methods=["POST"])
@htmx_login_required
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
