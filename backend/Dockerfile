FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python -m venv venv

# Upgrade pip
RUN venv/bin/pip install --upgrade pip setuptools wheel

# Copy requirements files for better caching
COPY requirements.txt prereq_requirements.txt ./

# Copy Plone constraints file if it exists
COPY constraints*.txt ./

# Install base Python dependencies from pip freeze
RUN venv/bin/pip install -r prereq_requirements.txt

# Install additional requirements
RUN venv/bin/pip install -r requirements.txt

# Copy all backend files
COPY . .

# Create necessary directories
RUN mkdir -p instance/var/filestorage \
    instance/var/blobstorage \
    instance/var/log \
    instance/var/cache \
    instance/etc/package-includes

# Create an empty instance directory structure
# The zope.conf will be generated on first run
RUN touch instance/.gitkeep

# Expose Plone port
EXPOSE 8080

# Use the virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Default command - run start_plone.py
CMD ["python", "start_plone.py"]