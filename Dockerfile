FROM python:3.11-slim

# Install system dependencies
# libreoffice: for document conversion
# default-jre: required by file converters (often needed by libreoffice or pdf tools)
# build-essential: for compiling python packages if needed
RUN apt-get update && apt-get install -y \
    libreoffice \
    default-jre \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
