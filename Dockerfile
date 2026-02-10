FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock* ./

# Use pip to install dependencies from pyproject.toml
RUN pip install --no-cache-dir -e .

# Copy application files (add more in the future as needed)
COPY main.py calendar_client.py ./
COPY templates/ ./templates/

# Set environment variables for Flask
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask app
CMD ["python", "main.py"]
