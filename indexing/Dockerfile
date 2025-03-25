FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for git and other potential requirements
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the setup script is executable
RUN chmod +x setup.sh

# Set the default command to run the setup script
CMD ["./setup.sh"]