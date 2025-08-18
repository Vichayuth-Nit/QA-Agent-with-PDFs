# Use official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the root of your project into the container
# This is crucial because your docker-compose.yml sets the build context to ./app
# but requirements.txt is at the project root. We need to copy it from the context
# into the /app directory inside the container before copying the rest of the app.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
# The context is ./app, so this copies main.py (and any other files in app/) to /app
COPY . .

# Expose port 8000, which your application will run on
EXPOSE 8000

# Command to run the application
# This CMD is here for standalone Docker runs, but it will be overridden by the
# 'command' in your docker-compose.yml when you use docker-compose up.
CMD ["uvicorn", "app.main:app", "--host", "localhost", "--port", "8000"]
