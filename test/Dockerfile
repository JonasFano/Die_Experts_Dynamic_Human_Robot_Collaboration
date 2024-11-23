FROM python:3.11

# Install Tkinter dependencies
RUN apt-get update && apt-get install -y python3-tk

# Copy the Python script
COPY hello_world.py /app/hello_world.py
WORKDIR /app

# Run the script
CMD ["python", "hello_world.py"]
