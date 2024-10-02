Deployment Steps:
1. Clone this repository
2. Within the infer.py file, update the client instantiation in line 34 with a real OpenAI API key. This update is required for Docker containerization.
3. Boot up Docker.
4. Within the CLI, set the working directory to the base of this repository.
5. Build the Docker image by running the following command: "docker build -t trially_container ."
6. Run the Docker container by running the following command: "docker run -p 8080:8080 -v trial_db:/app/trial_db trially_container"
