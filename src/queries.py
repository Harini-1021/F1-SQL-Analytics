import sqlite3
import pandas as pd

DB_PATH = "data/processed/f1.db" 

def run_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql,conn)
    conn.close()
    return df

if __name__ == "__main__":
    sql = """
    SELECT race_id, round, name, date
    FROM races
    WHERE year = 2021
    ORDER BY round;
    """
    df = run_query(sql)
    #print(df) 

    sql2 = """
    SELECT year, COUNT(*) AS num_races
    FROM races
    GROUP BY year
    ORDER BY year DESC
    LIMIT 10;
    """
    df2 = run_query(sql2)
    #print(df2)

    # Average points scored per race, across all results ever recorded
    sql3 = """
    SELECT ROUND(AVG(points),2) AS avg_points_per_result
    FROM results;
    """
    df3 = run_query(sql3)
    print(df3)

    # All races held in a specific date range - early season races across a few years
    sql4 = """
    SELECT name, date, year
    FROM races
    WHERE date BETWEEN '2020 - 01 -01' AND '2020-12-31'
    ORDER BY date;
    """
    df4 = run_query(sql4)
    #print(df4)

    # Race winners in 2023, with driver names 
    sql5 = """
    SELECT r.round, r.name AS race_name, d.forename, d.surname, res.points
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN drivers d ON res.driver_id = d.driver_id
    WHERE r.year = 2023 and res.position = 1
    ORDER BY r.round;
    """
    df5 = run_query(sql5)
    #print(df5)

    # continuing sql5 showing which constructor (team) each winner drove for
    sql6 = """
    SELECT r.round, r.name as race_name, d.surname AS driver, c.name AS team
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN drivers d ON res.driver_id = d.driver_id
    JOIN constructors c ON res.constructor_id = c.constructor_id
    WHERE r.year = 2023 AND res.position = 1
    ORDER BY r.round;
    """
    df6 = run_query(sql6)
    #print(df6) 

    # Wins per constructor, modern era(2014+), wit constructor nationality
    sql7 = """
    SELECT c.name AS constructor, c.nationality, COUNT(*) AS wins
    FROM results res
    JOIN  races r ON res.race_id = r.race_id
    JOIN  constructors c ON res.constructor_id = c.constructor_id
    WHERE res.position = 1 AND r.year >= 2014
    GROUP BY c.constructor_id
    ORDER BY wins DESC
    LIMIT 10;
    """
    df7 = run_query(sql7)
    print(df7)

