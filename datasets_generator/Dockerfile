FROM python:3.13.11-slim

# Install system dependencies for PostgreSQL client
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"


# Copiar archivos de configuración
COPY pyproject.toml .

# Instalar dependencias con uv
RUN mkdir -p /app/data/raw
RUN uv sync

# Copiar código de la aplicación
COPY generator.py .

# Punto de entrada para pasar argumentos
#ENTRYPOINT [ "uv", "run", "python", "generator.py","--mode","continuous"]
