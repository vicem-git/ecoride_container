from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
)
from datetime import datetime
from flask_login import login_required, current_user
from app.utils import static_id_resolver
from app.db_store import user_crud, trips_crud
from app.faker.villes import villes

pages_bp = Blueprint("pages", __name__, template_folder="../templates")


@pages_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
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
        user_id = user[0]

        user_roles = user_crud.get_user_roles(conn, user_id)

        return render_template(
            "pages/profile.html",
            page_wrap="profile",
            user_id=user_id,
            owner=owner,
            case=current_access,
            roles=user_roles,
        )


@pages_bp.route("/search_trips")
def search_trips():
    start_city = request.args.get("start_city")
    end_city = request.args.get("end_city")
    start_date = request.args.get("start_date") or datetime.now().isoformat()
    passenger_nr = request.args.get("passenger_nr")

    # NEED TO ESCAPE SMTH ?
    with current_app.db_manager.connection() as conn:
        trips = trips_crud.search_trips(
            conn,
            start_city=start_city,
            end_city=end_city,
            passenger_nr=passenger_nr,
            start_date=start_date,
        )

    return render_template(
        "pages/search_trips.html",
        page_wrap="search_trips",
        trips=trips,
        cities=list(villes.keys()),
    )


@pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")


@pages_bp.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", page_wrap="mentions_legales")
