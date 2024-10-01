'''Module for ingesting raw data from clinicaltrials.gov'''
import requests
import pandas as pd

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
                'NCT Id': nctId,
                'Brief Title': briefTitle,
                'Official Title': officialTitle,
                'Overall Status': overallStatus,
                'Conditions': conditions,
                'Interventions': interventions,
                'Study First Post Date': studyFirstPostDate,
                'Last Update Post Date': lastUpdatePostDate,
                'Phases': phases,
                'Study Type': studyType,
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
df = pd.DataFrame(data_list)

# TODO: Remove
# Print the DataFrame
print(f'DataFrame shape: {df.shape}')

# Save data to CSV
df.to_csv('clinical_trials_data.csv', index=False)
