FROM python:3.10-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --use-pep517 -r requirements.txt

# Expose the port Railway provides
EXPOSE $PORT

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
