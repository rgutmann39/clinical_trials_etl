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
from validate import (
    test_llm_inferences,
    GOLD_LABEL_NCT_IDS,
)
from flask import Flask
import os

REQUEST_PARAMS = {
    'query.cond': 'Cancer',
    # Note: Setting location to 'United States' inflates result quantity too much
    'query.locn': 'USA',
    'fields': 'protocolSection',
    'pageSize': 100,
}

app = Flask(__name__)

@app.route('/')
def main():
    db_path = 'trial_db'

    # INGEST
    # request raw data from clinicaltrials.gov
    print("Beginning ingestion.")
    raw_df = request_raw_data_from_api(request_params=REQUEST_PARAMS)
    # write raw data to DuckDB data table
    with duckdb.connect(db_path) as conn:
        commit_raw_data_to_duckdb(
            conn=conn,
            raw_df=raw_df,
        )
    print(f"Finishing ingestion.")

    # TRANSFORM
    # clean raw data
    print("Beginning transformation.")
    os.system('dbt run')
    print("Finishing transformation.")
    
    # INFER
    print("Beginning inference.")
    with duckdb.connect(db_path) as conn:
        # Materialize trial_data_transformed table in Pandas DataFrame to add new 'contains_chemo'
        # column before converting back to DuckDB.
        # Limiting quantity to 100 for reducing LLM calls
        inferred_df = conn.execute("SELECT * FROM trial_data_transformed limit 100").fetchdf()

        # aggregating intervention lists before passing strings to LLM
        aggregated_intervention_lists = [
            ', '.join(intervention)
            for intervention in inferred_df['interventionsArray']
        ]

        # Querying LLM to determine which interventions contain any chemotherapy
        inferred_df['contains_chemo'] = aggregated_contains_chemo(aggregated_intervention_lists)
        
        # commit new DuckDB table w/ LLM predictions about whether study contains chemotherapy
        commit_inferred_data_to_duckdb(
            conn=conn,
            inferred_df=inferred_df,
        )
        print("Finishing inference.")

        # VALIDATE
        print("Beginning validation.")
        where_clause = "'" + "', '".join(GOLD_LABEL_NCT_IDS) + "'"
        inference_df = conn.execute(
            "SELECT nctId, contains_chemo FROM trial_data_inferred " +
            f"WHERE nctId IN ({where_clause})"
        ).fetchdf()
        test_llm_inferences(inference_df)
        print("Finishing validation.")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Set the desired port here
    main()
