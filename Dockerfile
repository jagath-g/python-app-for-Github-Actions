# ---------- Stage 1: Build and Test ----------
FROM python:3.11-slim AS builder

# Install essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY requirements.txt requirements-dev.txt ./

# Install development dependencies (including pytest)
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application and test files
COPY app.py test_app.py ./

# Run tests and generate JUnit XML report
RUN pytest --junitxml=pytest-results.xml

# ---------- Stage 2: Production ----------
FROM python:3.11-slim AS production

WORKDIR /app

# Copy only necessary files for production
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose Flask app port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
