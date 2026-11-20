# 1. Imagen base oficial de Python ligera (slim) para reducir tamaño y superficie de ataque
FROM python:3.11-slim

# 2. Variables de entorno para optimizar la ejecución de Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUTA_ESTADISTICAS=/app/data/predicciones.jsonl

# 3. Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar primero el archivo de dependencias para aprovechar la caché de capas de Docker
COPY requirements.txt .

# 5. Instalar las dependencias necesarias sin almacenar caché de pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el código fuente de la aplicación, las pruebas y la interfaz web al contenedor
COPY model.py estadisticas.py app.py test_servicio.py ./
COPY templates/ ./templates/

# 6.1. Directorio donde se exportan las predicciones para el reporte de estadísticas
RUN mkdir -p /app/data

# 7. Ejecutar validación automatizada de los 4 estados clínicos durante el build
RUN python test_servicio.py

# 8. Documentar el puerto en el que el servicio escucha peticiones
EXPOSE 5000

# 9. Comando por defecto para iniciar el servicio cuando arranca el contenedor
CMD ["python", "app.py"]
