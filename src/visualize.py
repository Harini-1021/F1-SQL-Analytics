import matplotlib.pyplot as plt
import seaborn as sns
from queries import run_query

sns.set_theme(style = "darkgrid")

def plot_points_race_by_race(year: int, drivers: list[str]) -> None:
    """Line chart of cumulative championship points across a season,
    for the given list of driver surnames."""
    placeholders = ", ".join(f"'{d}'" for d in drivers)
    sql = f"""
    SELECT
        d.surname AS driver,
        r.round,
        SUM(res.points) OVER (
            PARTITION BY d.driver_id
            ORDER BY r.round
        ) AS cumulative_points
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN drivers d ON res.driver_id = d.driver_id
    WHERE r.year = {year} AND d.surname IN ({placeholders})
    ORDER BY d.surname, r.round;
    """
    df = run_query(sql)

    plt.figure(figsize = (10,6))
    sns.lineplot(data = df, x="round",y="cumulative_points",hue="driver",marker="o")
    plt.title(f"{year} Championship Points - Race by Race")
    plt.xlabel("Round")
    plt.ylabel("Cumulative Points")
    plt.tight_layout()
    plt.savefig("data/processed/points_race_by_race.png")
    plt.show()

def plot_constructor_wins(min_year: int = 2014) -> None:
    """Bar chart of total race wins per constructor, from min_year onward."""
    sql = f"""
    SELECT c.name AS constructor, COUNT(*) AS wins
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN constructors c ON res.constructor_id = c.constructor_id
    WHERE res.position = 1 AND r.year >= {min_year}
    GROUP BY c.constructor_id
    ORDER BY wins DESC;
    """
    df = run_query(sql)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="wins", y="constructor", hue="constructor", legend=False, palette="viridis")
    plt.title(f"Constructor Wins ({min_year}\u2013Present)")
    plt.xlabel("Wins")
    plt.ylabel("Constructor")
    plt.tight_layout()
    plt.savefig("data/processed/constructor_wins.png")
    plt.show()
    print("Saved chart to data/processed/constructor_wins.png")

def plot_grid_vs_finish(year: int) -> None:
    """Scatter plot: starting grid position vs finishing position for a season."""
    sql = f"""
    SELECT res.grid, res.position
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    WHERE r.year = {year} AND res.position IS NOT NULL AND res.grid > 0;
    """
    df = run_query(sql)

    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=df, x="grid", y="position", alpha=0.5)
    plt.plot([0, 20], [0, 20], linestyle="--", color="gray", label="Grid = Finish")
    plt.title(f"{year}: Grid Position vs. Finish Position")
    plt.xlabel("Starting Grid Position")
    plt.ylabel("Finishing Position")
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/processed/grid_vs_finish.png")
    plt.show()
    print("Saved chart to data/processed/grid_vs_finish.png")
    
if __name__ == "__main__":
    plot_points_race_by_race(2021, ["Hamilton", "Verstappen"])
    plot_constructor_wins(2014)
    plot_grid_vs_finish(2023)
