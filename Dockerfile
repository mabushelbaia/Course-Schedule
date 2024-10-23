FROM python:latest

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies if the requirements file has changed
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Make the script executable
RUN chmod +x /app/start_gunicorn.sh

# Expose the port
EXPOSE 8080

# Run the application
CMD ["./start_gunicorn.sh"]
