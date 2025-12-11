# Dockerfile for deploying the Gradio app
FROM python:3.12-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . /app

# Install Python deps
RUN python -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Expose the default Gradio port
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]
