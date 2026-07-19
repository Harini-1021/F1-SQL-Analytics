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

    # JOINS IN SQL 

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

 # COMMON TABLE EXPRESSIONS 
 
 # Which constructors had the biggest year-over-year swing in wins between two consecutive seasons?

 #Step 1: wins per constructor per season (as a CTE)
 # Step 2: filter down to only seasons with 10+ wins

    sql8 = """ 
    WITH constructor_wins_per_season AS(
    SELECT c.name AS constructor, r.year, COUNT(*) AS wins
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN constructors c ON res.constructor_id = c.constructor_id
    WHERE res.position = 1
    GROUP BY c.constructor_id, r.year
    )
    SELECT *
    FROM constructor_wins_per_season
    WHERE wins >= 10
    ORDER BY year, wins DESC;
    """ 
    df8 = run_query(sql8)
    #print(df8)  

# compare each row to that same constructor's prior year 
# Step 1 (CTE) : wins per constructor per season
# Step 2: join the CTE to itslef, marching each year to the previous year,
# to compute year-over-year change in wins

    # Step 1 (CTE): wins per constructor per season
    # Step 2: join the CTE to itself, matching each year to the previous year,
    #         to compute year-over-year change in wins
    sql9 = """
    WITH constructor_wins_per_season AS (
        SELECT c.constructor_id, c.name AS constructor, r.year, COUNT(*) AS wins
        FROM results res
        JOIN races r ON res.race_id = r.race_id
        JOIN constructors c ON res.constructor_id = c.constructor_id
        WHERE res.position = 1
        GROUP BY c.constructor_id, r.year
    )
    SELECT
        curr.constructor,
        curr.year,
        curr.wins AS wins_this_year,
        prev.wins AS wins_prev_year,
        curr.wins - prev.wins AS win_change
    FROM constructor_wins_per_season curr
    JOIN constructor_wins_per_season prev
        ON curr.constructor_id = prev.constructor_id
        AND curr.year = prev.year + 1
    ORDER BY win_change DESC
    LIMIT 10;
    """
    df9 = run_query(sql9)
    #print(df9)

# WINDOW FUNCTIONS

# Rewriting above query with LAG() function
    sql10 = """
    WITH constructor_wins_per_season AS(
    SELECT c.name AS constructor, r.year, COUNT(*) AS wins
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN constructors c ON res.constructor_id = c.constructor_id
    WHERE res.position = 1
    GROUP BY c.constructor_id, r.year
    )
    SELECT 
        constructor, 
        year,
        wins, 
        LAG(wins) OVER (PARTITION BY constructor ORDER BY year) AS wins_prev_year,
        wins - LAG(wins) OVER (PARTITION BY constructor ORDER BY year) AS win_change
        FROM constructor_wins_per_season
        ORDER BY win_change DESC
        LIMIT 10;
    """
    df10 = run_query(sql10)
    #print(df10)

# For each season, who finished as championship runner-up (2nd place in final standings)

    sql11 = """
    WITH season_points AS(
        SELECT d.surname AS driver, r.year, SUM(res.points) AS total_points
        FROM results res
        JOIN races r ON res.race_id = r.race_id
        JOIN drivers d ON res.driver_id = d.driver_id
        GROUP BY d.driver_id, r.year
    ),
    ranked_standings AS(
        SELECT 
            driver,
            year,
            total_points,
            RANK() OVER (PARTITION BY year ORDER BY total_points DESC) AS season_rank
        FROM season_points
    )
    SELECT year, driver, total_points
    FROM ranked_standings
    WHERE season_rank = 2
    ORDER BY year DESC
    LIMIT 10;
    """
    df11 = run_query(sql11)
    #print(df11)

# championship points accumulate race by race across a season

sql12 = """
SELECT 
    d.surname AS driver,
    r.round,
    r.name AS race_name,
    res.points,
    SUM(res.points) OVER (
        PARTITION BY d.driver_id
        ORDER BY r.round) AS cumulative_points
FROM results res
JOIN races r ON res.race_id = r.race_id
JOIN drivers d ON res.driver_id = d.driver_id
WHERE r.year = 2021 AND d.surname IN ('Hamilton','Verstappen')
ORDER BY d.surname, r.round;

"""
df12 = run_query(sql12)
print(df12)
