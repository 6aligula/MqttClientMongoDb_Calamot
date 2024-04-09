# Usa una imagen oficial de Python como imagen base
FROM python:3.9

# Establece el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Instala las dependencias de Python
# Asume que tienes un archivo requirements.txt con paho-mqtt y pymongo
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de tu aplicación al directorio de trabajo
COPY . .

# Comando para ejecutar tu aplicación
CMD ["python", "./app.py"]
