from pathlib import Path

import duckdb
import pandas as pd


class Database:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        # This depends where it is the DB
        self.db_path = base_dir / "data" / "warehouse" / "db.duckdb"

    def read_sql(self, query: str) -> pd.DataFrame:
        try:
            with duckdb.connect(self.db_path) as conn:
                df = conn.execute(query).fetchdf()
            return df
        except Exception as e:
            print(f"Error: {e}")
            return None
