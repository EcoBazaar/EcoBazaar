FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . ./

# Expose our contianer port
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 eco_bazaar.wsgi:application"]