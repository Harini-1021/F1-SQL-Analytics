import pandas as pd 

# Ergast CSVs use the literal string "\N" for NULL values 
# a leftover convention from their MySQL dump format.
# We tell pandas to treat it as NaN right at read-time.

NULL_VALUES = ["\\N"]

DATA_DIR ="data/raw/f1db_csv"

def explore_table(filename: str) -> pd.DataFrame:
    path = f"{DATA_DIR}/{filename}"
    df = pd.read_csv(path, na_values= NULL_VALUES)

    print(f"\n{'='*60}")
    print(f"{filename}")
    print(f"{'='*60}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"\nColumn dtypes:\n{df.dtypes}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nNull counts (non-zero only):")
    nulls = df.isnull().sum()
    print(nulls[nulls > 0] if nulls.sum() > 0 else "None")

    return df

if __name__ == "__main__":
    drivers = explore_table("drivers.csv")
    races = explore_table("races.csv")
    results = explore_table("results.csv")
    constructors = explore_table("constructors.csv")
    circuits = explore_table("circuits.csv")
    status = explore_table("status.csv")