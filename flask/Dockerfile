# Usa una imagen oficial de Python como imagen base
FROM python:3.9

# Establece un directorio de trabajo
WORKDIR /app

# Crea el directorio de logs antes de copiar los archivos
RUN mkdir -p /app/logs

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Establecer la variable de entorno para desactivar el buffering de Python
# dejar ENV PYTHONUNBUFFERED 1 en producción no es inherentemente malo y puede ser beneficioso para ciertos tipos de aplicaciones, 
# especialmente aquellas donde la inmediatez de la salida de logs es importante. 
ENV PYTHONUNBUFFERED 1

# Comando para ejecutar la aplicación usando Gunicorn
# CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5002", "main:app"]
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5002", "main:app"]

