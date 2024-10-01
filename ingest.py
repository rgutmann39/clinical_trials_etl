'''Module for ingesting raw data from clinicaltrials.gov'''
import requests
import pandas as pd
import duckdb
import os

_SUCCESSFUL_STATUS_CODE = 200
_COMPONENT_DELIMITER = '|'

# URL for API call
base_url = 'https://clinicaltrials.gov/api/v2/studies'
params = {
    # TODO: Update back to United States
    'query.locn': 'USA',
    'fields': 'protocolSection',
    'pageSize': 100,
}

# Initialize an empty list to store the data
data_list = []

# Loop through all pages of results
while True:
    # Print the current URL (for debugging purposes)
    print('Fetching data from:', base_url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()]))
    
    # Send a GET request to the API
    response = requests.get(base_url, params=params)

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
        params['pageToken'] = data.get('nextPageToken')
        if not params['pageToken']:
            break
    else:
        print('Failed to fetch data. Status code:', response.status_code)
        break

# Create a DataFrame from the list of dictionaries
trials_df = pd.DataFrame(data_list)

# # Save data to CSV
# trials_df.to_csv('clinical_trials_data.csv', index=False)

# Saving ingested data into DuckDB

# Connect to a DuckDB database file (it will be created if it doesn't exist)
conn = duckdb.connect('trially.trial_db')

# Create a new table with defined schema
conn.execute("""
CREATE TABLE IF NOT EXISTS trial_info (
    id INTEGER,
    name VARCHAR,
    age INTEGER
)
""")

# Populate the table from the Pandas DataFrame
conn.execute(
    "INSERT INTO trial_info SELECT * FROM trials_df",
    {'trials_df': trials_df}
)

# Commit the changes and close the connection
conn.commit()
conn.close()

# Start DuckDB in web mode
os.system("duckdb -web")
