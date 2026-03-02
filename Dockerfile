# Step 1: Use an official Python image from the Docker Hub
FROM python:3.8-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app/

# Step 4: Normalize line endings and ensure scripts are executable
RUN sed -i 's/\r$//' /app/wait-for-it.sh || true && chmod +x /app/wait-for-it.sh || true && chmod +x /app/wait-for-it-fixed.sh

# Step 5: Install the required dependencies in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y bash

# Step 6: Expose port 8000 for Django
EXPOSE 8000


# Step 7: Run the application using Django's manage.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]