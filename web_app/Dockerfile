# Use the official Python 3.12.0 base image
FROM python:3.12.0

# Set the working directory to /app
WORKDIR /web_app

COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the command to run on container start
CMD ["python", "app.py"]
