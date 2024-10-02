# Use the official Python image
FROM python:3.10

# # Set the working directory in the container
# WORKDIR /driver

ADD driver.py .
ADD ingest.py .
ADD infer.py .
ADD validate.py .
ADD models/trial_data_transformed.sql .

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port your app runs on
EXPOSE 8080

# Command to run the driver code
CMD ["python", "./driver.py"]
