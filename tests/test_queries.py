import sqlite3
import pytest 
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript("""
        CREATE TABLE drivers (driver_id INTEGER PRIMARY KEY, driver_ref TEXT,
            number INTEGER, code TEXT, forename TEXT, surname TEXT, dob DATE, nationality TEXT);
        CREATE TABLE constructors (constructor_id INTEGER PRIMARY KEY, constructor_ref TEXT,
            name TEXT, nationality TEXT);
        CREATE TABLE races (race_id INTEGER PRIMARY KEY, year INTEGER, round INTEGER,
            circuit_id INTEGER, name TEXT, date DATE);
        CREATE TABLE results (result_id INTEGER PRIMARY KEY, race_id INTEGER, driver_id INTEGER,
            constructor_id INTEGER, grid INTEGER, position INTEGER, position_order INTEGER,
            points REAL, laps INTEGER, milliseconds INTEGER, fastest_lap_time TEXT,
            fastest_lap_speed REAL, status_id INTEGER);
    """)

    # Two drivers, one constructor, two races, four results
    conn.executescript("""
       INSERT INTO drivers VALUES (1, 'hamilton', 44, 'HAM', 'Lewis', 'Hamilton', '1985-01-07', 'British');
        INSERT INTO drivers VALUES (2, 'verstappen', 33, 'VER', 'Max', 'Verstappen', '1997-09-30', 'Dutch');

        INSERT INTO constructors VALUES (1, 'mercedes', 'Mercedes', 'German');

        INSERT INTO races VALUES (1, 2021, 1, 1, 'Bahrain Grand Prix', '2021-03-28');
        INSERT INTO races VALUES (2, 2021, 2, 2, 'Emilia Romagna Grand Prix', '2021-04-18');

        INSERT INTO results VALUES (1, 1, 1, 1, 1, 1, 1, 25.0, 56, 5500000, NULL, NULL, 1);
        INSERT INTO results VALUES (2, 1, 2, 1, 2, 2, 2, 18.0, 56, 5510000, NULL, NULL, 1);
        INSERT INTO results VALUES (3, 2, 1, 1, 2, 1, 1, 25.0, 63, 6200000, NULL, NULL, 1);
        INSERT INTO results VALUES (4, 2, 2, 1, 1, NULL, 20, 0.0, 30, NULL, NULL, NULL, 3);
    """)
    conn.commit()
    yield conn
    conn.close()

def test_schema_has_expected_tables(test_db):
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type = 'table';",test_db
    )["name"].tolist()
    for expected in ["drivers","constructors","races","results"]:
        assert expected in tables

def test_driver_points_sum(test_db):
    """Hamilton's total points across both races should be exactly 50."""
    df = pd.read_sql_query("""
         SELECT SUM(points) as total FROM results WHERE driver_id =1;
    """,test_db)
    assert df["total"].iloc[0] == 50.0

def test_dnf_has_null_position(test_db):
    """A DNF (Verstappen, race 2) should have a NULL position but a real position_order."""
    df = pd.read_sql_query("""
        SELECT position, position_order FROM results WHERE result_id = 4;
    """,test_db)
    assert pd.isna(df["position"].iloc[0])
    assert df["position_order"].iloc[0] == 20

def test_cumulative_points_window_function(test_db):
    """Running total via SUM() OVER should correctly accumulate race by race."""
    df = pd.read_sql_query("""
        SELECT r.round, res.points, 
            SUM(res.points) OVER (PARTITION BY res.driver_id ORDER BY r.round) AS cumulative
        FROM results res
        JOIN races r ON res.race_id = r.race_id
        WHERE res.driver_id = 1
        ORDER BY r.round;
    """, test_db)
    assert df["cumulative"].tolist() == [25.0,50.0]

def test_rank_within_race(test_db):
    """RANK() should correctly order drivers by finishing position within a single race."""
    df = pd.read_sql_query("""
        SELECT driver_id, RANK() OVER (PARTITION BY race_id ORDER BY position_order) as pos_rank
        FROM results
        WHERE race_id = 1
        ORDER BY pos_rank;                
    """,test_db)
    assert df["pos_rank"].tolist() == [1,2]
    assert df["driver_id"].tolist() == [1,2]

def test_join_returns_driver_and_race_names(test_db):
    """A 3-table JOIN should correctly attach driver and race names to each result."""
    df = pd.read_sql_query("""
        SELECT d.surname, r.name AS race_name, res.points
        FROM results res
        JOIN drivers d ON res.driver_id = d.driver_id
        JOIN races r ON res.race_id = r.race_id
        WHERE res.result_id = 1;
    """, test_db)
    assert df["surname"].iloc[0] == "Hamilton"
    assert df["race_name"].iloc[0] == "Bahrain Grand Prix"
    assert df["points"].iloc[0] == 25.0


def test_cte_aggregates_points_per_driver_per_race(test_db):
    """A CTE computing per-race points should match a direct query, proving
    the CTE is just a named, reusable version of the same logic."""
    df = pd.read_sql_query("""
        WITH race_points AS (
            SELECT driver_id, race_id, points
            FROM results
            WHERE points > 0
        )
        SELECT driver_id, COUNT(*) AS races_scored_points
        FROM race_points
        GROUP BY driver_id
        ORDER BY driver_id;
    """, test_db)
    # Hamilton scored points in both races; Verstappen only in race 1
    assert df[df["driver_id"] == 1]["races_scored_points"].iloc[0] == 2
    assert df[df["driver_id"] == 2]["races_scored_points"].iloc[0] == 1