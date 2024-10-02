# Use the official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /driver

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Command to run the driver code
CMD ["python", "driver.py"]
