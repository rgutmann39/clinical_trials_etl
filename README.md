This repository contains a data pipeline that performs the following actions:
1. Ingest clinical trial data from clinicaltrials.gov (ingest.py)
2. Transform raw data to structured data (models/trial_data_transformed.sql)
3. Infer whether a clinical trial contains any chemotherapy inverventions using a call to an LLM (infer.py)
4. Validate the accuracy of the LLM precitions on a subset of 20 verified trials (validate.py)

The pipeline logic is orchestrated within driver.py.
The application can also be converted into a Docker container for maximum portability.

Steps to Run Application in a Docker Container:
1. Clone this repository
2. Within the infer.py file, update the client instantiation in line 34 with a real OpenAI API key. This update is required for Docker containerization.
3. Boot up Docker.
4. Within the CLI, set the working directory to the base of this repository.
5. Build the Docker image by running the following command: "docker build -t trially_container ."
6. Run the Docker container by running the following command: "docker run -p 8080:8080 -v trial_db:/app/trial_db trially_container"