# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0

RUN pip3 install --no-cache-dir -r machine-learning-client/requirements.txt

# Run play.py when the container launches
CMD ["python3", "play.py"]
