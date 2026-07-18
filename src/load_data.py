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

def load_races(conn: sqlite3.Connection) -> None:
    """Load races.csv -> races table.

    Cleaning needed:
    - date: parse to real datetime, store as ISO string (YYYY-MM-DD)
    - drop session-timing columns (fp1/fp2/fp3/quali/sprint) not in our schema
    """
    df = pd.read_csv(f"{RAW_DIR}/races.csv", na_values=NULL_VALUES)
    df = df.rename(columns={"raceId": "race_id", "circuitId": "circuit_id"})

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    df = df[["race_id", "year", "round", "circuit_id", "name", "date"]]

    df.to_sql("races", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into races")

def load_results(conn: sqlite3.Connection) -> None:
    """Load results.csv -> results table. The fact table — depends on
    drivers, races, constructors, and status all being loaded first.

    Note: position/laps/fastestLap appear as float64 in pandas (not int64)
    purely because NaN forces an upcast from int to float. SQLite will still
    store/query them correctly against our INTEGER schema columns.
    """
    df = pd.read_csv(f"{RAW_DIR}/results.csv", na_values=NULL_VALUES)
    df = df.rename(columns={
        "resultId": "result_id",
        "raceId": "race_id",
        "driverId": "driver_id",
        "constructorId": "constructor_id",
        "positionOrder": "position_order",
        "fastestLap": "fastest_lap",
        "fastestLapTime": "fastest_lap_time",
        "fastestLapSpeed": "fastest_lap_speed",
        "statusId": "status_id",
    })

    df = df[[
        "result_id", "race_id", "driver_id", "constructor_id", "grid",
        "position", "position_order", "points", "laps", "milliseconds",
        "fastest_lap_time", "fastest_lap_speed", "status_id",
    ]]

    df.to_sql("results", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into results")

if __name__ == "__main__":
    reset_database()
    conn = get_connection()
    load_status(conn)
    load_constructors(conn)
    load_circuits(conn)
    load_drivers(conn)
    load_races(conn)
    load_results(conn)
    conn.commit()
    conn.close()
    print("connection committed and closed")
