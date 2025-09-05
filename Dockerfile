FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app

EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "60", "-b", "0.0.0.0:5000", "--access-logfile", "-", "src.app:app"]

