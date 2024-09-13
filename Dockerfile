FROM python:latest

# Set the working directory
WORKDIR /app

COPY . .

# Install dependencies
RUN pip install -r requirements.txt 
RUN chmod +x /app/start_gunicorn.sh

EXPOSE 8080

# Run the application
CMD ["./start_gunicorn.sh"]