# Use python:3-slim as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Git
RUN apt-get update && apt-get install -y git

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 3000

# Run app.py when the container launches
CMD ["python3", "crawling.py"]
