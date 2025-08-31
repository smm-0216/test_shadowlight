import duckdb

DB_PATH = r"C:\\Users\\santi\\OneDrive\\Documentos\\ShadowLight\\data\\warehouse\\db.duckdb"
CSV_PATH = r"C:\\Users\\santi\\OneDrive\\Documentos\\ShadowLight\\data\\enriched\\enriched.csv"
TABLE = "ads_spend"

csv = CSV_PATH.replace("\\", "/")
con = duckdb.connect(DB_PATH)
con.sql(f"CREATE TABLE IF NOT EXISTS {TABLE} AS SELECT * FROM read_csv_auto('{csv}') LIMIT 0;")
con.sql(f"COPY {TABLE} FROM '{csv}' (AUTO_DETECT TRUE, HEADER TRUE);")
con.close()
