# Use Python base image
FROM python:3.11.9

# Install system dependencie
RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    libx11-xcb1 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxrandr2 \
    libxfixes3 \
    libxinerama1 \
    libxcb1 \
    libxcb-glx0 \
    libxcb-shm0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-render-util0 \
    libxcb-render0 \
    libxrender1 \
    libgl1-mesa-glx \
    libxi6 \
    libxtst6 \
    libsm6 \
    x11-utils \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /safety_monitor_prev

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Command to run the camera vision program
CMD ["python", "ui.py"],
