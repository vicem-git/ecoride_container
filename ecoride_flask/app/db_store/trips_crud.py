from psycopg.rows import dict_row
from datetime import datetime
import json
from geopy.distance import geodesic


def reverse_lookup_coords(lat, lng):
    villes = {
        "Paris": {"lat": 48.85341, "lng": 2.34880},
        "Marseille": {"lat": 43.29695, "lng": 5.38107},
        "Lyon": {"lat": 45.74846, "lng": 4.84671},
        "Toulouse": {"lat": 43.60426, "lng": 1.44367},
        "Nice": {"lat": 43.70313, "lng": 7.26608},
        "Nantes": {"lat": 47.21725, "lng": -1.55336},
        "Strasbourg": {"lat": 48.58392, "lng": 7.74553},
        "Montpellier": {"lat": 43.61092, "lng": 3.87723},
        "Bordeaux": {"lat": 44.84044, "lng": -0.58050},
        "Lille": {"lat": 50.63297, "lng": 3.05858},
        "Rennes": {"lat": 48.11198, "lng": -1.67429},
        "Reims": {"lat": 49.25000, "lng": 4.03333},
        "Le Havre": {"lat": 49.49380, "lng": 0.10767},
        "Grenoble": {"lat": 45.17155, "lng": 5.72239},
        "Dijon": {"lat": 47.31667, "lng": 5.01667},
    }
    for city, coords in villes.items():
        if abs(coords["lat"] - lat) < 0.05 and abs(coords["lng"] - lng) < 0.05:
            return city
    return "Unknown"


def create_tripp(conn, trip_data):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO trips 
            (driver_id, vehicle_id,
            start_location, 
            end_location, start_time, 
            price, trip_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id""",
            (
                trip_data["driver_id"],
                trip_data["start_location"],
                trip_data["end_location"],
                trip_data["start_time"],
                trip_data["end_time"],
                trip_data["price"],
                trip_data["trip_status"],
            ),
        )
        trip_id = cur.fetchone()[0]
        conn.commit()
        return trip_id


def get_trip_by_id(conn, trip_id):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM trips WHERE id = %s", (trip_id,))
        trip_data = cur.fetchone()
        return trip_data if trip_data else None


def update_trip_status(conn, trip_id, new_status):
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("UPDATE trips SET status = %s WHERE id = %s", (new_status, trip_id))
        conn.commit()
        return True


def get_trip_available_seats(conn, trip_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT available_seats
            FROM trip_available_seats
            WHERE trip_id = %s
            """,
            (trip_id,),
        )
        result = cur.fetchone()
        available_seats = result[0] if result else None
        return available_seats


def get_passenger_trips(conn, user_id, status=None):
    with conn.cursor(row_factory=dict_row) as cur:
        query = """
            SELECT *
            FROM trip_with_status_and_summary t
            JOIN trip_passengers tp ON t.id = tp.trip_id
            WHERE tp.passenger_id = %s
            ORDER BY t.start_time DESC
        """
        params = [user_id]
        if status:
            query += " AND t.status = %s"
            params.append(status)
        query += "ORDER BY t.start_time DESC"
        cur.execute(query, params)
        trips = cur.fetchall()
        return trips if trips else None


def get_driver_trips(conn, driver_id, status=None):
    with conn.cursor(row_factory=dict_row) as cur:
        query = """
            SELECT *
            FROM trip_with_status_and_summary
            WHERE driver_id = %s
        """
        params = [driver_id]
        if status:
            query += " AND status = %s"
            params.append(status)
        query += " ORDER BY start_time DESC"
        cur.execute(query, params)
        trips = cur.fetchall()
        return trips if trips else None


def set_trip_rating(conn, trip_id, rating):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE trips SET rating = %s WHERE id = %s",
            (rating, trip_id),
        )
        conn.commit()
        return True


def search_trips(
    conn,
    start_city=None,
    end_city=None,
    passenger_nr=None,
    max_price=None,
    start_date=None,
):
    query = """
        SELECT s.*
        FROM trip_summaries s
        WHERE 1=1
    """
    params = []

    if start_city:
        query += " AND s.summary->>'start_city' = %s"
        params.append(start_city)

    if end_city:
        query += " AND s.summary->>'end_city' = %s"
        params.append(end_city)

    if max_price:
        query += " AND (s.summary->>'price')::int <= %s"
        params.append(max_price)

    if start_date and start_date.lower() != "none":
        query += " AND (s.summary->>'start_time')::timestamp >= %s"
        params.append(start_date)

    query += " ORDER BY (s.summary->>'start_time')::timestamp ASC"

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        trips = cur.fetchall()

    for trip in trips:
        trip_id = trip.get("trip_id")
        trip["available_seats"] = get_trip_available_seats(conn, trip_id)

    if passenger_nr:
        passenger_nr = int(passenger_nr)
        trips = [trip for trip in trips if trip["available_seats"] >= int(passenger_nr)]

    return trips if trips else None


def get_trip_summary(conn, trip_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT s.*
            FROM trip_summaries s
            WHERE s.trip_id = %s
            """,
            (trip_id,),
        )
        trip_summary = cur.fetchone()
        return trip_summary if trip_summary else None


def generate_trip_summary(conn, trip_id, commit=True):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                t.id,
                ST_Y(t.start_location::geometry),
                ST_X(t.start_location::geometry),
                ST_Y(t.end_location::geometry),
                ST_X(t.end_location::geometry),
                t.start_time,
                t.price,
                d.rating,
                v.plate_number,
                v.model,
                v.color,
                b.name AS brand,
                e.name AS energy,
                u.username AS driver_name
            FROM trips t
            JOIN driver_data d ON t.driver_id = d.id
            JOIN users u ON d.user_id = u.id
            JOIN vehicles v ON t.vehicle_id = v.id
            JOIN vehicle_brand b ON v.brand = b.id
            JOIN energy_types e ON v.energy_type = e.id
            WHERE t.id = %s
        """,
            (trip_id,),
        )

        row = cur.fetchone()
        if not row:
            raise ValueError(f"No trip found with ID: {trip_id}")

        (
            trip_id,
            start_lat,
            start_lng,
            end_lat,
            end_lng,
            start_time,
            price,
            rating,
            plate,
            model,
            color,
            brand,
            energy,
            driver_name,
        ) = row

        distance_km = geodesic((start_lat, start_lng), (end_lat, end_lng)).kilometers
        speed = 60 + (hash(trip_id) % 30)
        duration_min = round((distance_km / speed) * 60)

        start_city = reverse_lookup_coords(start_lat, start_lng)
        end_city = reverse_lookup_coords(end_lat, end_lng)

        summary = {
            "start_city": start_city,
            "end_city": end_city,
            "start_time": start_time.isoformat(),
            "distance_km": round(distance_km, 2),
            "estimated_duration_min": duration_min,
            "price": price,
            "vehicle": {
                "brand": brand,
                "model": model,
                "energy": energy,
                "color": color,
                "plate": plate,
            },
            "driver_name": driver_name,
            "driver_rating": rating,
        }

        cur.execute(
            "INSERT INTO trip_summaries (trip_id, summary) VALUES (%s, %s) ON CONFLICT (trip_id) DO UPDATE SET summary = EXCLUDED.summary",
            (trip_id, json.dumps(summary)),
        )
        if commit:
            conn.commit()


def regenerate_all_missing_summaries(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id
            FROM trips t
            LEFT JOIN trip_summaries s ON s.trip_id = t.id
            WHERE s.trip_id IS NULL
        """)
        trip_ids = [row[0] for row in cur.fetchall()]

    counter = 0
    for trip_id in trip_ids:
        generate_trip_summary(conn, trip_id)
        counter += 1

    return counter
