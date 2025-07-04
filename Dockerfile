# Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY . .

# Umgebungsvariablen
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    SECRET_KEY="changeme" \
    SQLALCHEMY_DATABASE_URI="sqlite:///fitness.db"

# Port
EXPOSE 8000

# Start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]