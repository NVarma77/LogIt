# Development image. A slimmer production image (gunicorn, collectstatic, non-root user)
# comes with the deploy slice.
FROM python:3.12-slim

# Unbuffered so logs appear immediately; no .pyc files in the mounted source folder.
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first so this layer is cached until requirements change.
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
