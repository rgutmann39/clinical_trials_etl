"""Driver module to orchestrate pipeline workflow"""
import duckdb
from ingest import (
    request_raw_data_from_api,
    commit_raw_data_to_duckdb,
)
from infer import (
    aggregated_contains_chemo,
    commit_inferred_data_to_duckdb,
)
import os

REQUEST_PARAMS = {
    'query.cond': 'Cancer',
    'query.locn': 'USA',
    'fields': 'protocolSection',
    'pageSize': 100,
}

def main():
    db_path = 'trial_db'

    # INGEST
    # request raw data from clinicaltrials.gov
    raw_df = request_raw_data_from_api(request_params=REQUEST_PARAMS)
    # write raw data to DuckDB data table
    with duckdb.connect(db_path) as conn:
        commit_raw_data_to_duckdb(
            conn=conn,
            raw_df=raw_df,
        )

    # TRANSFORM
    # clean raw data
    os.system('dbt run')
    
    # INFER
    with duckdb.connect(db_path) as conn:
        # Materialize trial_data_transformed table in Pandas DataFrame to add new 'contains_chemo'
        # column before converting back to DuckDB
        # TODO: Remove limit statement
        # inferred_df = conn.execute("SELECT * FROM trial_data_transformed").fetchdf()
        inferred_df = conn.execute("SELECT * FROM trial_data_transformed limit 15").fetchdf()


        # cleaning intervention lists before passing strings to LLM
        aggregated_intervention_lists = [
            ', '.join(intervention)
            for intervention in inferred_df['interventionsArray']
        ]

        # Querying LLM to determine which interventions contain chemo
        inferred_df['contains_chemo'] = aggregated_contains_chemo(aggregated_intervention_lists)
        commit_inferred_data_to_duckdb(
            conn=conn,
            inferred_df=inferred_df,
        )

        # trial_data_inferred = conn.execute("SELECT * FROM trial_data_inferred").fetchall()
        # print(trial_data_inferred)


if __name__ == "__main__":
    main()
