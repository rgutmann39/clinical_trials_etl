"""Driver module to orchestrate pipeline workflow"""
import duckdb
from ingest import ingest_data

# Establish DuckDB connection
conn = duckdb.connect('trially.trial_db')

# INGEST
ingest_data(conn=conn)

result = conn.execute("SELECT COUNT(*) FROM trial_data_raw").fetchall()

print(result[0][0])

# Close the connection
conn.close()