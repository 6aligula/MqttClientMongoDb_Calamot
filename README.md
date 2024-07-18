# Smart Garden

## Descripción

Este proyecto está diseñado para monitorear y controlar la humedad y temperatura en un sistema de jardinería. Utiliza sensores conectados a microcontroladores ESP8266, y la información se transmite y almacena en una base de datos MongoDB. La aplicación web proporciona una interfaz para visualizar los datos y controlar un motor.

## Estructura del Proyecto

La estructura del proyecto es la siguiente:

```
MqttClientMongoDb_Calamot
│
├── arduino
│   ├── dht11_mqtt
│   │   └── dht11_mqtt.ino
│   ├── motor_esp8266
│   │   └── motor_esp8266.ino
│   └── sensor_humedad
│       ├── notes.md
│       └── sensor_humedad.ino
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── config
│   └── mosquitto.conf
├── docker-compose.yml
├── flask
│   ├── Dockerfile
│   ├── MotorConfig.py
│   ├── db_config.py
│   ├── main.py
│   ├── mqtt_config.py
│   ├── requirements.txt
│   ├── settings.py
│   └── tempHumedad.py
├── frontend
│   ├── Dockerfile
│   ├── public
│   ├── src
│   ├── package.json
│   └── package-lock.json
├── logs
│   └── app.log
└── nginx
    └── default.conf
```

## Capturas de la Aplicación Web

### Interfaz Principal

![Garden](image.png)

### Configuración y Control del Motor

![alt text](image-1.png)

## Instrucciones para Trabajar con MongoDB en Docker

Para explorar y trabajar con una base de datos MongoDB desde un contenedor de Docker, puedes utilizar varias herramientas y métodos. Aquí te explico cómo puedes hacerlo:

### 1. Usar la línea de comandos de MongoDB

Primero, necesitas conectarte al contenedor de MongoDB usando un terminal. Puedes hacerlo con el comando `docker exec`:

```bash
docker exec -it mongodb bash
```

Reemplaza `mongodb` con el nombre o ID de tu contenedor de MongoDB si es diferente. Una vez dentro del contenedor, puedes iniciar una sesión de MongoDB utilizando el cliente de línea de comandos `mongo`:

```bash
mongo -u mongoadmin -p
```

Serás promovido a ingresar la contraseña. Una vez dentro del cliente de MongoDB, puedes usar comandos de MongoDB para explorar la base de datos:

- **Listar todas las bases de datos**:
  ```mongo
  show dbs
  ```
- **Cambiar a una base de datos específica**:
  ```mongo
  use motor_database
  ```
- **Listar colecciones en la base de datos actual**:
  ```mongo
  show collections
  ```
- **Ver documentos en una colección**:
  ```mongo
  db.estados_calefaccion.find().pretty()
  ```
  Este comando muestra los documentos en la colección `estados_calefaccion` de forma legible.

### 2. Usar una herramienta GUI

Para una gestión más visual de tu base de datos MongoDB dentro de Docker, puedes utilizar herramientas GUI como Compass o Robo 3T. Para conectar estas herramientas a tu contenedor de MongoDB, debes asegurarte de que los puertos de MongoDB están correctamente expuestos y mapeados en tu archivo `docker-compose.yml`. Luego puedes conectar tu herramienta GUI usando la dirección IP del host Docker y el puerto mapeado, junto con las credenciales de usuario.

Por ejemplo, si tienes la siguiente configuración en `docker-compose.yml`:

```yaml
mongodb:
  image: mongo:4.4
  ports:
    - "27017:27017"
```

Puedes conectar tu herramienta GUI a `localhost:27017` (o la dirección IP de tu máquina Docker si estás en un entorno de nube o virtualizado), usando las credenciales especificadas.

### 3. Acceder a MongoDB desde otra aplicación

Si estás desarrollando una aplicación que necesita acceder a MongoDB, simplemente utiliza la cadena de conexión apropiada que referencia el nombre del servicio Docker, como `mongodb`, como host en tus cadenas de conexión, por ejemplo:

```python
client = MongoClient("mongodb://username:password@mongodb:27017/motor_database")
```

Asegúrate de que tu aplicación también esté ejecutándose en un contenedor dentro del mismo `docker-compose.yml` o en la misma red Docker para que pueda resolver el nombre del servicio `mongodb`.

Estos métodos te permitirán gestionar y explorar tu base de datos MongoDB dentro de un contenedor de Docker eficazmente.

## Notas Adicionales

- El estado del motor funciona con WebSockets.
- Toda la aplicación está dockerizada, excepto el código de los ESP8266 que se encuentra en Arduino.
