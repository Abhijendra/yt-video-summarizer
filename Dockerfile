# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (documentation only)
EXPOSE 5000

# Command to run the application using a production WSGI server (
CMD ["python","app.py"]
