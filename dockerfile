FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto que usa Cloud Run
EXPOSE 8080

# Comando para iniciar
CMD ["uvicorn", "webhook:app", "--host", "0.0.0.0", "--port", "8080"]