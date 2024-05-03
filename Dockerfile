# Usa la imagen oficial de Mosquitto como base
FROM eclipse-mosquitto:latest

# Copia tu archivo de configuración personalizado
COPY ./config/mosquitto.conf /mosquitto/config/mosquitto.conf

# Genera dinámicamente el archivo de contraseñas y añade el usuario admin con su contraseña
RUN touch /mosquitto/config/mosquitto_passwd \
    && mosquitto_passwd -b /mosquitto/config/mosquitto_passwd admin lokodeldiablo

# Establece los permisos recomendados para el archivo de contraseñas
RUN chmod 0700 /mosquitto/config/mosquitto_passwd