from psycopg.rows import dict_row


def get_driver_data(conn, user_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, rating FROM driver_data WHERE user_id = %s",
            (user_id,),
        )
        driver_data = cur.fetchone()
        return driver_data if driver_data else None


def create_driver(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO driver_data (user_id) VALUES (%s) RETURNING id", (user_id,)
        )
        driver_id = cur.fetchone()[0]
        return driver_id


def set_driver_preferences(conn, driver_id, preferences):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM driver_preferences WHERE driver_id = %s", (driver_id,))
        for preference in preferences:
            cur.execute(
                "INSERT INTO driver_preferences (driver_id, preference_id) VALUES (%s, %s)",
                (driver_id, preference),
            )
        conn.commit()
        return True


def get_driver_preferences(conn, driver_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT p.name FROM preferences p JOIN driver_preferences dp ON dp.preference_id = p.id WHERE dp.driver_id = %s",
            (driver_id,),
        )
        current_preferences = cur.fetchall()
        return current_preferences if current_preferences else None


def get_all_driver_preferences(conn):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, name FROM preferences ORDER BY name")
        preferences = cur.fetchall()
        return preferences if preferences else None


def add_vehicles(conn, driver_id, vehicle_data):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO vehicles (driver_id, model, registration_date, plate_number, color, number_of_seats, brand, energy_type_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                driver_id,
                vehicle_data["model"],
                vehicle_data["registration_date"],
                vehicle_data["plate_number"],
                vehicle_data["color"],
                vehicle_data["number_of_seats"],
                vehicle_data["brand"],
                vehicle_data["energy_type"],
            ),
        )
        conn.commit()
        return True


def remove_vehicles(conn, driver_id, vehicle_ids):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM vehicles WHERE driver_id = %s AND id = ANY(%s)",
            (driver_id, vehicle_ids),
        )
        conn.commit()
        return True


def get_driver_vehicles(conn, driver_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT v.id, v.model, v.registration_date, v.plate_number, v.color, v.number_of_seats, b.name AS brand, e.name AS energy_type FROM vehicles v JOIN vehicle_brand b ON v.brand = b.id JOIN energy_types e ON v.energy_type_id = e.id WHERE v.driver_id = %s",
            (driver_id,),
        )
        vehicles = cur.fetchall()
        return vehicles if vehicles else None


def get_vehicle_by_id(conn, vehicle_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT v.id, v.driver_id, v.registration_date, v.plate_number, v.color, v.number_of_seats, b.name AS brand, e.name AS energy_type FROM vehicles v JOIN vehicle_brand b ON v.brand = b.id JOIN energy_types e ON v.energy_type_id = e.id WHERE v.id = %s",
            (vehicle_id,),
        )
        vehicle = cur.fetchone()
        return vehicle if vehicle else None


def set_driver_rating(conn, driver_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT rating FROM trips WHERE driver_id = %s AND rating > 0", (driver_id,)
        )
        all_ratings = cur.fetchall()

        if not all_ratings:
            average = 0
        else:
            average = sum(int(x[0]) for x in all_ratings) / len(all_ratings)

        cur.execute(
            "UPDATE driver_data SET rating = %s WHERE user_id = %s",
            (average, driver_id),
        )
        conn.commit()


def get_vehicle_brands(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, name FROM vehicle_brand ORDER BY name")
        brands = cur.fetchall()
        return brands if brands else None


def get_energy_types(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, name FROM energy_types ORDER BY name")
        energy_types = cur.fetchall()
        return energy_types if energy_types else None
