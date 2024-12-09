# Use the official Python image as a base image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files
# and to enable Python stdout and stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the build context to the container
COPY --from=requirements requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . /app/

# Expose port 5000 for Flask-SocketIO
EXPOSE 5000

# Define the command to run the Flask-SocketIO application
CMD ["python", "-m", "server.py"]