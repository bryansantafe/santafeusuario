FROM python:3.12-slim

# Instalar dependencias del sistema nativas para WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto para Gunicorn
EXPOSE 8002

# Comando para encender la app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server.wsgi:application"]