# Use a specific Python version compatible with pyodbc
FROM python:3.9-slim

# Install system dependencies for pyodbc
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    unixodbc-dev \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Install ODBC drivers
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    libodbc1 \
    odbcinst \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Set the command to run your application
CMD ["python", "function_app.py"]

