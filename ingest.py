'''Module for ingesting raw data from clinicaltrials.gov'''
import requests
import pandas as pd
import duckdb
from typing import Any, Mapping

_SUCCESSFUL_STATUS_CODE = 200
_COMPONENT_DELIMITER = '|'
_BASE_URL = 'https://clinicaltrials.gov/api/v2/studies'

def _request_raw_data_from_api(
    request_params: Mapping[str, Any],
) -> pd.DataFrame:
    data_list = []

    # Loop through all pages of results
    while True:
        # Print the current URL (for debugging purposes)
        print('Fetching data from:', _BASE_URL + '?' + '&'.join([f'{k}={v}' for k, v in request_params.items()]))
        
        # Send a GET request to the API
        response = requests.get(_BASE_URL, params=request_params)

        # Check if the request was successful
        if response.status_code == _SUCCESSFUL_STATUS_CODE:
            data = response.json()  # Parse JSON response into data entries
            studies = data.get('studies', [])  # Extract the list of studies

            # Loop through each study and extract specific information
            for study in studies:
                nctId = study['protocolSection']['identificationModule'].get('nctId', '')
                briefTitle = study['protocolSection']['identificationModule'].get('briefTitle', '')
                officialTitle = study['protocolSection']['identificationModule'].get('officialTitle', '')
                overallStatus = study['protocolSection']['statusModule'].get('overallStatus', '')
                conditions = _COMPONENT_DELIMITER.join(study['protocolSection'].get('conditionsModule', {}).get('conditions', []))
                interventions_list = study['protocolSection'].get('armsInterventionsModule', {}).get('armGroups', [])
                interventions = _COMPONENT_DELIMITER.join(
                    [
                        intervention.get('interventionNames')[0]
                        if 'interventionNames' in intervention
                        else ''
                        for intervention in interventions_list
                    ]
                )
                studyFirstPostDate = study['protocolSection']['statusModule'].get('studyFirstPostDateStruct', {}).get('date', '')
                lastUpdatePostDate = study['protocolSection']['statusModule'].get('lastUpdatePostDateStruct', {}).get('date', '')
                phases = _COMPONENT_DELIMITER.join(study['protocolSection'].get('designModule', {}).get('phases', []))
                studyType = study['protocolSection'].get('designModule', {}).get('studyType', [])
                sex = study['protocolSection'].get('eligibilityModule', {}).get('sex', '')
                minimumAge = study['protocolSection'].get('eligibilityModule', {}).get('minimumAge', '')
                maximumAge = study['protocolSection'].get('eligibilityModule', {}).get('maximumAge', '')

                # Append the data to the list as a dictionary
                data_list.append({
                    'nctId': nctId,
                    'briefTitle': briefTitle,
                    'officialTitle': officialTitle,
                    'overallStatus': overallStatus,
                    'conditions': conditions,
                    'interventions': interventions,
                    'studyFirstPostDate': studyFirstPostDate,
                    'lastUpdatePostDate': lastUpdatePostDate,
                    'phases': phases,
                    'studyType': studyType,
                    'sex': sex,
                    'minimumAge': minimumAge,
                    'maximumAge': maximumAge,
                })

            # If next page exists, update page token. Else, break out of loop
            request_params['pageToken'] = data.get('nextPageToken')
            if not request_params['pageToken']:
                break
        else:
            print('Failed to fetch data. Status code:', response.status_code)
            break

    # Create a DataFrame from the list of dictionaries
    raw_data_df = pd.DataFrame(data_list)
    return raw_data_df


def _save_raw_data_to_duckdb(
    conn: duckdb.DuckDBPyConnection,
    raw_data_df: pd.DataFrame,
) -> None:
    """Saves raw data from Padas DataFrame into 'trial_data_raw' DuckDB table"""
    # TODO: remove
    # # Save data to CSV
    # trials_df.to_csv('clinical_trials_data.csv', index=False)

    # Define schema for raw data table
    conn.execute("""
    CREATE OR REPLACE TABLE trial_data_raw (
        nctId VARCHAR,
        briefTitle VARCHAR,
        officialTitle VARCHAR,
        overallStatus VARCHAR,
        conditions VARCHAR,
        interventions VARCHAR,
        studyFirstPostDate VARCHAR,
        lastUpdatePostDate VARCHAR,
        phases VARCHAR,
        studyType VARCHAR,
        sex VARCHAR,
        minimumAge VARCHAR,
        maximumAge VARCHAR
    )
    """)

    # Populate the table from the Pandas DataFrame
    conn.execute(
        f"INSERT INTO trial_data_raw SELECT * FROM raw_data_df"
    )

    # Commit the transaction to save changes
    conn.commit()


def ingest_data(
    conn: duckdb.DuckDBPyConnection,
    request_params: Mapping[str, Any] = {
        # TODO: Update back to United States
        'query.locn': 'USA',
        'fields': 'protocolSection',
        'pageSize': 100,
    },
) -> None:
    raw_data_df = _request_raw_data_from_api(
        request_params=request_params,
    )
    _save_raw_data_to_duckdb(
        conn=conn,
        raw_data_df=raw_data_df,
    )
