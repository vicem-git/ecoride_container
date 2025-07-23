from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    redirect,
    url_for,
)
import datetime
from flask_login import login_required, current_user
from app.utils import static_id_resolver
from app.db_store import user_crud, driver_crud
from app.faker.villes import villes

pages_bp = Blueprint("pages", __name__, template_folder="../templates")

current_time = datetime.datetime.now().strftime("%c")


@pages_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
        current_time=current_time,
        page_wrap="home",
        cities=list(villes.keys()),
    )


@pages_bp.route("/registration")
def registration():
    return render_template("pages/registration.html", page_wrap="register")


@pages_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")


@pages_bp.route("/profile/<user_id>")
@login_required
def profile(user_id):
    current_access = str(current_user.account_access_id)
    current_access = static_id_resolver("account_access", current_access)

    owner = str(current_user.user_id) == str(user_id)

    with current_app.db_manager.connection() as conn:
        user = user_crud.get_user_by_account_id(conn, current_user.id)

        if not user:
            flash("User not found. Please complete onboarding.")
            return redirect(url_for("pages.onboard"))

        user_roles = user_crud.get_user_roles(conn, user_id)

        print(f"User roles: {user_roles}")
        driver_info = {}

        if "driver" in user_roles:
            driver_data = driver_crud.get_driver_data(conn, user_id)
            print(f"Driver data: {driver_data}")

            if not driver_data:
                new_driver = driver_crud.create_driver(conn, user_id)
                print(f"New driver created: {new_driver}")

            driver_id = driver_data["id"]
            print(f"Driver ID: {driver_id}")

            if driver_data:
                driver_preferences = driver_crud.get_driver_preferences(conn, driver_id)
                driver_vehicles = driver_crud.get_driver_vehicles(conn, driver_id)

                driver_info = {
                    "data": driver_data,
                    "preferences": driver_preferences,
                    "vehicles": driver_vehicles,
                }

            print(f"Driver info: {driver_info}")

        return render_template(
            "pages/profile.html",
            current_time=current_time,
            page_wrap="profile",
            user_id=user_id,
            owner=owner,
            case=current_access,
            roles=user_roles,
            driver_info=driver_info,
        )


@pages_bp.route("/search_trips")
def search_trips():
    return render_template(
        "pages/search_trips.html", page_wrap="search_trips", cities=list(villes.keys())
    )


@pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")
