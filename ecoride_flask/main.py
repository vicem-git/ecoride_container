from flask import Flask
from rich.logging import RichHandler
import logging
from app.db_store import DatabaseManager, crud_utilities, trips_crud
from app.routes import pages_bp
from app.routes.api import auth_bp, users_bp, drivers_bp, trips_bp
from config import db_config, Config
from app.utils import bcrypt, login_manager, safe_close, fr_date
from app.models import session_user_loader
import atexit
from datetime import datetime
import locale
from app.faker import seed_data

# Might raise error on some systems, TEST FOR DOCKER
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")


def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
    )

    app.jinja_env.filters["fr_date"] = fr_date

    # CONTEXT PROCESSOR TEST
    # use to inject variables into templates globally
    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now().year}

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(markup=True)],
    )

    # MAYBE UNCOMMENT IN PROD
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.config.from_object(Config)
    bcrypt.init_app(app)
    db_manager = DatabaseManager(db_config)
    app.db_manager = db_manager

    logging.info(
        f"[bold green]TIME NOW : {datetime.now().strftime('%d %B %Y - %H:%Mhs')}[/bold green]"
    )

    try:
        app.static_ids = crud_utilities.load_static_ids(db_manager)
        logging.info("static ids loaded ~")
    except Exception as e:
        logging.error(f"failed to load static ids: {str(e)}")

    try:
        with db_manager.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]
                conn.commit()
            if user_count < 10:
                seed_data(conn, num_drivers=1000, num_users=3000, trips_per_driver=5)
                logging.info("DB SEED : Database seeded.")
            else:
                logging.info("DB SEED : Seeding skipped: users already exist.")

        with db_manager.connection() as conn:
            count = trips_crud.regenerate_all_missing_summaries(conn)
            if count:
                logging.info(f"BATCH SUMMARIES: {count} summaries generated.")
            else:
                logging.info(
                    "BATCH SUMMARIES: Summary generation skipped: data already present."
                )

    except Exception as e:
        logging.error(f"❌ Seeding error: {e}")

    login_manager.init_app(app)
    session_user_loader(app)

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(trips_bp)

    login_manager.login_view = "pages.login"

    # SAFE CLOSING ON EXIT
    atexit.register(safe_close, app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
