# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container for the application code
WORKDIR /usr/src/app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt ./

# Install the required ML libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY app.py ./

# Make sure the script is executable
RUN chmod +x app.py

# Create the /work directory where data will be read/written
RUN mkdir /work

# Set the script as the entrypoint
ENTRYPOINT ["python", "./app.py"]
