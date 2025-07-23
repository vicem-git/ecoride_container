from flask import current_app
from psycopg import sql
from psycopg.rows import dict_row


def test_connection(conn):
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            return result[0] == 1
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def configure_conn(conn, schema_name):
    try:
        with conn.cursor() as cur:
            query = sql.SQL("SET search_path TO {}").format(sql.Identifier(schema_name))
            cur.execute(query)
            print(f"Search path set to : {schema_name}")
    except Exception as e:
        print(f"Failed to set search path: {e}")
        raise


STATIC_TABLES = [
    "account_access",
    "account_status",
    "roles",
    "preferences",
    "vehicle_brand",
    "energy_types",
    "review_status",
    "trip_status",
]


def load_static_ids(db_manager):
    ids = {}
    with db_manager.connection() as conn:
        conn.autocommit = True
        with conn.cursor(row_factory=dict_row) as cur:
            for table in STATIC_TABLES:
                cur.execute(f"SELECT name, id FROM {table};")
                ids[table] = {row["name"]: str(row["id"]) for row in cur.fetchall()}

    return ids
