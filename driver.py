"""Driver module to orchestrate pipeline workflow"""
import duckdb
from ingest import (
    request_raw_data_from_api,
    commit_raw_data_to_duckdb,
)
import os


def main():
    db_path = 'trial_db'

    # INGEST
    raw_data_df = request_raw_data_from_api()
    with duckdb.connect(db_path) as conn:
        commit_raw_data_to_duckdb(
            conn=conn,
            raw_data_df=raw_data_df,
        )
        # result = conn.execute("SELECT count(*) FROM trial_data_raw").fetchall()
        # print(result[0][0])

    # TRANSFORM
    os.system('dbt run')
        


if __name__ == "__main__":
    main()
