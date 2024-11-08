# Clinical Trials Data Pipeline: ETL, LLM Integration, Docker
This ETL data pipeline pulls raw data from [clinicaltrials.gov](clinicaltrials.gov), cleans the data, and integrates with OpenAI's LLM API to infer additional trial information. The full application is available to run in a Docker Container.

## Technologies
Python, SQL, dbt, Docker, LLM API calls

## Pipeline Components
### Extraction
Extract clinical trial data from [clinicaltrials.gov](clinicaltrials.gov) using a web API (ingest.py)

### Transformation
Transform raw data to structured data (models/trial_data_transformed.sql)

### Inference
Integration with LLM API to infer whether a clinical trial likely contains any chemotherapy interventions (infer.py)

### Validation
Validate the accuracy of the LLM predictions (validate.py)

### Pipeline Orchestration
Execute full pipeline logic sequentially (driver.py)


## How to Run Application in a Docker Container
1. Clone this repository.
2. Within the CLI, set the working directory to the base of this repository.
3. Within the infer.py file, update the client instantiation in line 34 with a real OpenAI API key. This update is required for Docker containerization.
4. Ensure that Docker is running.
6. Build the Docker image by running the following command: "docker build -t clinical_trials_container ."
7. Verify that the Docker image was successfully built by running: "docker image ls | grep clinical_trials_container". If this returns a line starting with "clinical_trials_container", the build was successful.
8. Run the Docker container by running the following command: "docker run -p 8080:8080 -v trial_db:/app/trial_db clinical_trials_container"
9. If the run hangs after several seconds with a message ending in "... Press CTRL+C to quit", continue the pipeline execution by pressing CTRL+C exactly once.
