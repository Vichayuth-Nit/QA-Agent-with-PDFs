# Use official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the root of your project into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose port 8000, which your application will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "localhost", "--port", "8000"]
