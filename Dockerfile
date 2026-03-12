FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir -e .

# Copy application source
COPY run.py ./
COPY app/ ./app/
COPY data/ ./data/

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask app via the entry point
CMD ["python", "run.py"]
