import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "data/processed/f1.db"
RAW_DIR = "data/raw/f1db_csv"

NULL_VALUES = ["\\N"]

def get_connection() ->sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(" PRAGMA foreign_keys = ON;")
    print(f"Connected to: {Path(DB_PATH).resolve()}")
    return conn

def reset_database() -> None:
    db_file = Path(DB_PATH)
    if db_file.exists():
        db_file.unlink()
        print(f"Removed existing database at {DB_PATH}")
    with open("src/schema.sql","r") as f:
        schema_sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)
    conn.close()
    print("Rebuilt empty schema")

def load_status(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(f"{RAW_DIR}/status.csv",na_values=NULL_VALUES)
    df = df.rename(columns={"statusId":"status_id"})
    df.to_sql("status",conn,if_exists="append",index=False)
    print(f"Loaded {len(df)} rows into status") 

def load_constructors(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(f"{RAW_DIR}/constructors.csv",na_values=NULL_VALUES)
    df = df.rename(columns={
        "constructorId":"constructor_id",
        "constructorRef": "constructor_ref",
    })
    df = df[["constructor_id","constructor_ref","name","nationality"]]

    df.to_sql("constructors",conn,if_exists="append",index=False)
    print(f"Loaded {len(df)} rows into constrcutors")

def load_circuits(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(f"{RAW_DIR}/circuits.csv",na_values=NULL_VALUES)
    df = df.rename(columns={
        "circuitId": "circuit_id",
        "circuitRef": "circuit_ref",
    })
    df = df[["circuit_id","circuit_ref","name","location","country","lat","lng","alt"]]
    df.to_sql("circuits",conn,if_exists="append",index=False)
    print(f"Loaded {len(df)} rows into circuits") 

def load_drivers(conn: sqlite3.Connection) -> None:
    """Load drivers.csv -> drivers table.

    Cleaning needed:
    - number/code: already NaN via na_values, will write as NULL
    - dob: parse to a real datetime, then store as ISO-format string (YYYY-MM-DD)
    """
    df = pd.read_csv(f"{RAW_DIR}/drivers.csv",na_values=NULL_VALUES)
    df = df.rename(columns={
        "driverId":"driver_id",
        "driverRef":"driver_ref",
                   })
    df["dob"] = pd.to_datetime(df["dob"],errors="coerce").dt.strftime("%Y-%m-%d")

    df = df[["driver_id","driver_ref","number","code","forename","surname","dob","nationality"]]

    df.to_sql("drivers",conn,if_exists="append",index=False)
    print(f"Loaded {len(df)} rows into drivers")

if __name__ == "__main__":
    reset_database()
    conn = get_connection()
    load_status(conn)
    load_constructors(conn)
    load_circuits(conn)
    load_drivers(conn)
    conn.commit()
    conn.close()
    print("connection committed and closed")
