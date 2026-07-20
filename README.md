# F1 SQL Analytics

A SQL-first analytics tool built on 75 years of Formula 1 historical data — demonstrating a full pipeline from raw CSVs to a normalized relational schema to SQL analysis (joins, CTEs, window functions) to visualization.

## Architecture — star schema
<svg viewBox="0 0 900 560" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">
  <rect width="900" height="560" fill="#ffffff"/>

  <!-- Arrow marker -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666666"/>
    </marker>
  </defs>

  <!-- Title -->
  <text x="450" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#222222">F1 SQL Analytics — Star Schema</text>

  <!-- circuits box -->
  <rect x="40" y="90" width="150" height="60" rx="8" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="115" y="115" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">circuits</text>
  <text x="115" y="134" text-anchor="middle" font-size="12" fill="#5b6b7a">dimension</text>

  <!-- races box -->
  <rect x="260" y="90" width="150" height="60" rx="8" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="335" y="115" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">races</text>
  <text x="335" y="134" text-anchor="middle" font-size="12" fill="#5b6b7a">dimension</text>

  <!-- drivers box -->
  <rect x="40" y="250" width="150" height="60" rx="8" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="115" y="275" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">drivers</text>
  <text x="115" y="294" text-anchor="middle" font-size="12" fill="#5b6b7a">dimension</text>

  <!-- constructors box -->
  <rect x="710" y="250" width="150" height="60" rx="8" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="785" y="275" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">constructors</text>
  <text x="785" y="294" text-anchor="middle" font-size="12" fill="#5b6b7a">dimension</text>

  <!-- status box -->
  <rect x="375" y="440" width="150" height="60" rx="8" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="450" y="465" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">status</text>
  <text x="450" y="484" text-anchor="middle" font-size="12" fill="#5b6b7a">dimension</text>

  <!-- results FACT box (center) -->
  <rect x="345" y="240" width="210" height="80" rx="10" fill="#4c72b0" stroke="#2c4a70" stroke-width="2.5"/>
  <text x="450" y="272" text-anchor="middle" font-size="17" font-weight="bold" fill="#ffffff">results</text>
  <text x="450" y="294" text-anchor="middle" font-size="12" fill="#dbe6f5">FACT TABLE — one row per</text>
  <text x="450" y="309" text-anchor="middle" font-size="12" fill="#dbe6f5">driver, per race</text>

  <!-- Arrow: circuits -> races -->
  <line x1="190" y1="120" x2="255" y2="120" stroke="#666666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow: races -> results -->
  <path d="M335,150 L335,220 Q335,240 355,247" fill="none" stroke="#666666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow: drivers -> results -->
  <line x1="190" y1="280" x2="340" y2="280" stroke="#666666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow: constructors -> results -->
  <line x1="710" y1="280" x2="560" y2="280" stroke="#666666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow: status -> results -->
  <path d="M450,440 L450,325" fill="none" stroke="#666666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Legend -->
  <rect x="40" y="500" width="16" height="16" fill="#eef2f7" stroke="#5b7ba6" stroke-width="2"/>
  <text x="64" y="513" font-size="12" fill="#444444">Dimension table (describes an entity)</text>
  <rect x="330" y="500" width="16" height="16" fill="#4c72b0" stroke="#2c4a70" stroke-width="2"/>
  <text x="354" y="513" font-size="12" fill="#444444">Fact table (records an event)</text>
</svg>

`results` is the fact table — one row per driver, per race. Everything else describes an entity (who, where, why), not an event. This shape is the same pattern used in real analytics warehouses (a sales fact table surrounded by customer/product/store dimensions) — F1 results stand in for any general operational analytics problem.

| Table | Rows | Role |
|---|---|---|
| `drivers` | 861 | dimension |
| `constructors` | 212 | dimension |
| `circuits` | 77 | dimension |
| `status` | 139 | dimension (finish/DNF reason lookup) |
| `races` | 1,125 | dimension (season/round/circuit) |
| `results` | 26,759 | **fact** — one row per driver per race |

## Tech stack & key decisions

- **Raw `sqlite3`**, not SQLAlchemy — the project's purpose is to demonstrate hand-written SQL (joins, CTEs, window functions), not an ORM's query builder. For a single-developer local analytics tool, this is the right tradeoff; a production system needing multi-backend support would reasonably choose SQLAlchemy instead.
- **pandas** for cleaning (at load time) and as the DataFrame container query results land in.
- **matplotlib / seaborn** for visualization.
- **pytest**, with an in-memory (`:memory:`) fixture database — fast, deterministic, and requires no downloaded data to run.

## Setup

```bash
git clone <your-repo-url>
cd f1-sql-analytics
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Download the dataset (raw CSVs are not committed to this repo):
1. Get the "Formula 1 World Championship (1950–2024)" dataset from Kaggle
2. Extract it into `data/raw/f1db_csv/`

Build and load the database:
```bash
python src/load_data.py
```

Run tests:
```bash
pytest tests/ -v
```

## Usage — CLI

```bash
python src/main.py wins --min-year 2018
python src/main.py points --year 2021 --drivers Hamilton Verstappen
python src/main.py grid --year 2023
python src/main.py --help
```

## Example queries

**Window function — cumulative championship points, race by race:**
```sql
SELECT
    d.surname AS driver,
    r.round,
    SUM(res.points) OVER (
        PARTITION BY d.driver_id ORDER BY r.round
    ) AS cumulative_points
FROM results res
JOIN races r ON res.race_id = r.race_id
JOIN drivers d ON res.driver_id = d.driver_id
WHERE r.year = 2021 AND d.surname IN ('Hamilton', 'Verstappen');
```

**CTE + window function — championship runner-up by season:**
```sql
WITH season_points AS (
    SELECT d.surname AS driver, r.year, SUM(res.points) AS total_points
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    JOIN drivers d ON res.driver_id = d.driver_id
    GROUP BY d.driver_id, r.year
),
ranked_standings AS (
    SELECT driver, year, total_points,
        RANK() OVER (PARTITION BY year ORDER BY total_points DESC) AS season_rank
    FROM season_points
)
SELECT year, driver, total_points
FROM ranked_standings
WHERE season_rank = 2
ORDER BY year DESC;
```

**Self-join → replaced by `LAG()`** — see `src/queries.py` for both versions side by side; a good example of how window functions simplify logic that would otherwise require a self-join.

## Sample output

![Grid vs Finish Position, 2023]((assets/grid_vs_finish.png)png)

Points below the diagonal line gained positions during the race; points above lost positions. Starting position predicts finishing position most strongly at the extremes of the grid — the midfield (positions 6–15) shows far more volatility.

## Known limitations

- **Sprint race points (2021+) are not included.** Points totals are computed from `results` only; `sprint_results.csv` was not loaded, so season point totals in 2021+ will be slightly lower than official standings (verified against the 2021 Hamilton/Verstappen title fight — our totals were off by ~2–7 points due to this gap).
- Session-timing metadata (FP1/FP2/FP3/qualifying/sprint timestamps) was intentionally excluded from the `races` schema — not needed for the analytical questions this project answers.

## What I'd add next

- Load `sprint_results.csv` and union sprint points into season totals
- A `pit_stops`/`lap_times`-driven analysis (lap-by-lap gap to leader, using `LAG()`)
- Parameterize queries properly (`?` placeholders) instead of f-string interpolation, to eliminate the SQL-injection-shaped pattern currently used for driver-name filtering
- CI (GitHub Actions) running `pytest` on every push
EOF

