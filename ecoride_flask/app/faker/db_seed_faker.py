from psycopg import sql
from faker import Faker
from uuid import uuid4
import random
from app.faker.villes import villes
import logging

# MODULE LOGGER
logger = logging.getLogger(__name__)

fake = Faker("fr_FR")

car_models = [
    ("citadine", 4),  # city car
    ("berline", 5),  # sedan
    ("coupé", 2),
    ("break", 5),  # station wagon
    ("minivan", 7),  # minivan
    ("SUV", 5),
    ("cabriolé", 2),  # convertible
    ("fourgon", 3),  # van
]


def random_ville():
    city = random.choice(list(villes.keys()))
    coords = villes[city]
    return {
        "label": city,
        "lat": coords["lat"],
        "lng": coords["lng"],
    }


def is_value_unique(cur, table, column, value):
    query = sql.SQL("SELECT 1 FROM {table} WHERE {column} = %s LIMIT 1").format(
        table=sql.Identifier(table),
        column=sql.Identifier(column),
    )
    cur.execute(query, (value,))
    return cur.fetchone() is None


def get_unique_email(cur, max_attempts=20):
    for _ in range(max_attempts):
        email = fake.email()
        if is_value_unique(cur, "accounts", "email", email):
            return email
    raise ValueError("Unable to generate unique email")


def get_unique_username(cur, max_attempts=20):
    for _ in range(max_attempts):
        username = fake.user_name()
        if is_value_unique(cur, "users", "username", username):
            return username
    raise ValueError("Unable to generate unique username")


def get_unique_license_plate(cur, max_attempts=20):
    for _ in range(max_attempts):
        plate = fake.license_plate()
        if is_value_unique(cur, "vehicles", "plate_number", plate):
            return plate
    raise ValueError("Unable to generate unique license plate")


def get_id(cur, table, name):
    query = sql.SQL("SELECT id FROM {table} WHERE name = %s").format(
        table=sql.Identifier(table)
    )
    cur.execute(query, (name,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"No ID found for name '{name}' in table '{table}'")
    return row[0]


def seed_data(conn, num_drivers=1000, num_users=1500, trips_per_driver=5):
    try:
        with conn.cursor() as cur:
            # Get static IDs
            access_id = get_id(cur, "account_access", "user")
            status_id = get_id(cur, "account_status", "active")
            driver_role_id = get_id(cur, "roles", "driver")
            passenger_role_id = get_id(cur, "roles", "passenger")
            cur.execute("SELECT id FROM trip_status")
            trip_status_ids = [row[0] for row in cur.fetchall()]

            # Create users
            passenger_ids = []
            for _ in range(num_users):
                email = get_unique_email(cur)
                username = get_unique_username(cur)
                account_id = str(uuid4())
                user_id = str(uuid4())
                cur.execute(
                    "INSERT INTO accounts (id, email, password_hash, account_access_id, account_status_id) VALUES (%s, %s, %s, %s, %s)",
                    (account_id, email, "fakehash", access_id, status_id),
                )
                cur.execute(
                    "INSERT INTO users (id, account_id, username) VALUES (%s, %s, %s)",
                    (user_id, account_id, username),
                )
                cur.execute(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                    (user_id, passenger_role_id),
                )
                passenger_ids.append(user_id)

            # Create drivers and trips
            for _ in range(num_drivers):
                account_id = str(uuid4())
                user_id = str(uuid4())
                email = get_unique_email(cur)
                username = get_unique_username(cur)
                cur.execute(
                    "INSERT INTO accounts (id, email, password_hash, account_access_id, account_status_id) VALUES (%s, %s, %s, %s, %s)",
                    (account_id, email, "fakehash", access_id, status_id),
                )
                cur.execute(
                    "INSERT INTO users (id, account_id, username) VALUES (%s, %s, %s)",
                    (user_id, account_id, username),
                )
                cur.execute(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                    (user_id, driver_role_id),
                )

                driver_id = str(uuid4())
                cur.execute(
                    "INSERT INTO driver_data (id, user_id, rating) VALUES (%s, %s, %s)",
                    (driver_id, user_id, random.randint(3, 5)),
                )

                # Get random brand and energy
                cur.execute("SELECT id FROM vehicle_brand ORDER BY RANDOM() LIMIT 1")
                brand_id = cur.fetchone()[0]
                cur.execute("SELECT id FROM energy_types ORDER BY RANDOM() LIMIT 1")
                energy_id = cur.fetchone()[0]
                license_plate = get_unique_license_plate(cur)
                vehicle_id = str(uuid4())
                model, max_seats = random.choice(car_models)
                cur.execute(
                    """
                    INSERT INTO vehicles (
                        id, driver_id, plate_number, registration_date, brand, model, color, number_of_seats, energy_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        vehicle_id,
                        driver_id,
                        license_plate,
                        fake.date_between(start_date="-3y", end_date="-1y"),
                        brand_id,
                        model,
                        fake.color_name(),
                        max_seats,
                        energy_id,
                    ),
                )

                # Insert trips for this driver
                for _ in range(trips_per_driver):
                    start = random_ville()
                    end = random_ville()
                    trip_id = str(uuid4())
                    start_lat, start_lng = start["lat"], start["lng"]
                    end_lat, end_lng = end["lat"], end["lng"]
                    start_time = fake.date_time_between(
                        start_date="+1d", end_date="+30d"
                    )
                    price = random.randint(5, 30)
                    trip_status = random.choice(trip_status_ids)

                    cur.execute(
                        """
                        INSERT INTO trips (
                            id, driver_id, vehicle_id,
                            start_location, end_location,
                            start_time, price, trip_status
                        ) VALUES (
                            %s, %s, %s,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                            %s, %s, %s
                        )
                    """,
                        (
                            trip_id,
                            driver_id,
                            vehicle_id,
                            start_lng,
                            start_lat,
                            end_lng,
                            end_lat,
                            start_time,
                            price,
                            trip_status,
                        ),
                    )

                    cur.execute(
                        "SELECT number_of_seats FROM vehicles WHERE id = %s",
                        (vehicle_id,),
                    )
                    max_passengers = cur.fetchone()[0]

                    num_passengers = random.randint(1, min(3, max_passengers))
                    chosen_passengers = random.sample(passenger_ids, num_passengers)

                    for pid in chosen_passengers:
                        cur.execute(
                            "INSERT INTO trip_passengers (trip_id, user_id) VALUES (%s, %s)",
                            (trip_id, pid),
                        )

                    # Add reviews
                    for pid in chosen_passengers:
                        review_id = str(uuid4())
                        rating = random.randint(3, 5)
                        comment = fake.sentence()
                        review_status_id = get_id(cur, "review_status", "approved")
                        cur.execute(
                            """
                            INSERT INTO reviews (
                                id, trip_id, author_id, rating, comments, review_status_id
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                            (
                                review_id,
                                trip_id,
                                pid,
                                rating,
                                comment,
                                review_status_id,
                            ),
                        )

        conn.commit()
    except Exception as e:
        logger.error(f"DB SEED ERROR : {e}")
        raise
