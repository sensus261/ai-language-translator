FROM python:3.9-slim

# Set environment variables to prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

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

# Run the application with unbuffered output
CMD ["python", "-u", "app.py"]