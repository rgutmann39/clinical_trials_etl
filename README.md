# Data Pipelining and LLM Integration for Clinical Trial Data

## Overview
### Extract
Extract clinical trial data from clinicaltrials.gov using a web API (ingest.py)

### Transform
Transform raw data to structured data (models/trial_data_transformed.sql)

### Infer
Integration with LLM API to infer whether a clinical trial likely contains any chemotherapy interventions (infer.py)

### Validate
Validate the accuracy of the LLM predictions (validate.py)

The pipeline logic is orchestrated within driver.py.
The application can also be converted into a Docker container for maximum portability.

Steps to Run Application in a Docker Container:
1. Clone this repository
2. Within the CLI, set the working directory to the base of this repository.
3. Within the infer.py file, update the client instantiation in line 34 with a real OpenAI API key. This update is required for Docker containerization.
4. Boot up Docker.
6. Build the Docker image by running the following command: "docker build -t trially_container ."
7. Verify that the Docker image was successfully built by running: "docker image ls | grep trially_container". If this returns a line starting with "trially_container", the build was successful.
8. Run the Docker container by running the following command: "docker run -p 8080:8080 -v trial_db:/app/trial_db trially_container"
9. If the run hangs after several seconds with a message ending in "... Press CTRL+C to quit", continue the pipeline execution by pressing CTRL+C exactly once.

Next Steps Toward Productionization of this Pipeline:
1. Batching of inputs during LLM calls: Since inference is currently the time bottleneck, batching of inputs would produce a significant time speed-up.
2. More expansive LLM testing and prompt engineering: Before associating an attribute with a trial in a production setting, the level of confidence in the prediction should be increased by increasing the size of the gold set and iterating on the prompt until a suitable accuracy has been achieved.
3. Easier pipeline orchestration: Since the pipeline workload scales with the number of trials queried, wrapping the pipeline in an Airflow DAG would make the pipeline orchestration easier once the workloads were larger. This would also abstract away the role of the driver module since Airflow manages task dependencies.
