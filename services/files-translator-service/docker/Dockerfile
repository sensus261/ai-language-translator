FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama and other dependencies
RUN pip install ollama flask tqdm python-dotenv

# Set the working directory
WORKDIR /app

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]