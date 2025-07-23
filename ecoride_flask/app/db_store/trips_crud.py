from psycopg.rows import dict_row


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


def get_user_trips(conn, user_id, status):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT t.*
            FROM trips t
            JOIN trip_passengers tp ON t.id = tp.trip_id
            WHERE tp.user_id = %s AND t.trip_status = %s
        """,
            (user_id, status),
        )
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


def list_trips(
    conn,
    near_start=None,
    near_end=None,
    max_dist_km=10,
    status=None,
    start_after=None,
    max_price=None,
    sort_by=None,
):
    conn.autocommit = True
    with conn.cursor(row_factory=dict_row) as cur:
        query = "SELECT * FROM trips WHERE TRUE"
        params = []

        if near_start:
            query += (
                " AND ST_DWithin(start_location, ST_MakePoint(%s), %s)::geography, %s"
            )
            params += [near_start["lng"], near_start["lat"], max_dist_km * 1000]
        if near_end:
            query += (
                " AND ST_DWithin(end_location, ST_MakePoint(%s), %s)::geography, %s"
            )
            params += [near_end["lng"], near_end["lat"], max_dist_km * 1000]

        if status:
            query += " AND trip_status = %s"
            params.append(status)

        if start_after:
            query += " AND start_time >= %s"
            params.append(start_after)

        if max_price:
            query += " AND price <= %s"
            params.append(max_price)

        if sort_by == "start_time":
            query += " ORDER BY start_time ASC"
        elif sort_by == "price":
            query += " ORDER BY price ASC"

        cur.execute(query, params)
        trips_found = cur.fetchall()
        return trips_found if trips_found else None


def search_trip_summaries(
    conn, start_city=None, end_city=None, max_price=None, start_date=None
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
        return cur.fetchall()
