# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY main.py .

# Make port 8909 available to the world outside this container
EXPOSE 8909

# Run main.py when the container launches
CMD ["python", "main.py"]
