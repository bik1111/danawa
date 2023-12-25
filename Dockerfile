# Use the official PyTorch image as a base image
FROM pytorch/pytorch:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Git
RUN apt-get update && apt-get install -y git

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 3000

# PyKoSpacing 설치
RUN pip install git+https://github.com/haven-jeon/PyKoSpacing.git

# Run app.py when the container launches
CMD ["python", "crawling.py"]
