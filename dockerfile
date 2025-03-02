# Use official Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY requirements.txt requirements.txt
COPY scripts/ scripts/
COPY dbt_project/ dbt_project/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for Superset (8088)
EXPOSE 8088

# Command to keep container running
CMD ["tail", "-f", "/dev/null"]
