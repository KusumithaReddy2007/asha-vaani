
from sqlalchemy import inspect, text
from app.database.session import engine

columns = {
    "house_number": "VARCHAR(100)",
    "location_lat": "FLOAT",
    "location_lng": "FLOAT",
    "location_address": "VARCHAR(500)",
}
inspector = inspect(engine)
if "healthcare_visits" not in inspector.get_table_names():
    raise RuntimeError("healthcare_visits table not found")
existing = {c["name"] for c in inspector.get_columns("healthcare_visits")}
with engine.begin() as conn:
    for name, sql_type in columns.items():
        if name not in existing:
            conn.execute(text(f"ALTER TABLE healthcare_visits ADD COLUMN {name} {sql_type}"))
            print("Added:", name)
        else:
            print("Already exists:", name)
