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

    sql3 = """
    SELECT ROUND(AVG(points),2) AS avg_points_per_result
    FROM results;
    """
    df3 = run_query(sql3)
    print(df3)

    sql4 = """
    SELECT name, date, year
    FROM races
    WHERE date BETWEEN '2020 - 01 -01' AND '2020-12-31'
    ORDER BY date;
    """
    df4 = run_query(sql4)
    print(df4)