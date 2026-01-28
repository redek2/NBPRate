# Use an official lightweight Python image.
# Matches local development version (3.13) to ensure consistency.
FROM python:3.13-slim

# Set the working directory in the container.
WORKDIR /app

# Set environment variables:
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disc.
# PYTHONUNBUFFERED: Ensures python output is sent straight to terminal (logs visibility).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies.
# We copy requirements.txt first to leverage Docker layer caching.
COPY requirements.txt .

# Install dependencies with no cache to keep the image small.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 8000 to the outside world.
EXPOSE 8000

# Run the application using Uvicorn server.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]