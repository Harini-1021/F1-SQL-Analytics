import sqlite3
from pathlib import Path

DB_PATH = "data/processed/f1.db"
SCHEMA_PATH = "src/schema.sql"

def build_schema() -> None:
    """ Create the SQLite database file and apply schema.sql to it."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_PATH,"r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    print(f"Datebase created at {DB_PATH}")

if __name__ == "__main__":
    build_schema()
    