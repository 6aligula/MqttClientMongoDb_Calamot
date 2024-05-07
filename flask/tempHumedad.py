#tempHumedad.py
from flask import Flask, jsonify
from mqtt_config import create_mqtt_client
import os
from db_config import get_mongo_client, get_database

# Carga las variables de entorno desde el archivo .env
app = Flask(__name__)

# Configura los detalles del broker MQTT
temperatura_topic = os.getenv("TEMP_TOPIC")
humedad_topic = os.getenv("HUME_TOPIC")

# Configuración de MongoDB modificada para usar variables de entorno
mongo_client = get_mongo_client()
db = get_database(mongo_client, 'sensor_database')
temperature_collection = db['temperatura']
humidity_collection = db['humedad']

# Callback para cuando el cliente recibe una CONNACK del servidor
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(temperatura_topic)
    client.subscribe(humedad_topic)

# Callback que se llama cuando se recibe un mensaje del servidor.
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    if msg.topic == temperatura_topic:
        print(msg.topic + " " + payload)
        temperature_collection.insert_one({"temperatura": float(payload)})

    elif msg.topic == humedad_topic:
        print(msg.topic + " " + payload)
        humidity_collection.insert_one({"humedad": float(payload)})

client = create_mqtt_client(on_connect, on_message)

def setup_temperature_routes(app):
    @app.route('/temperatura')
    def get_temperature():
        temperatures = temperature_collection.find().sort("_id", -1).limit(10)
        # Convertir cada ObjectId a string
        result = [{"temperatura": temp["temperatura"], "id": str(temp["_id"])} for temp in temperatures]
        return jsonify(result)

    @app.route('/humedad')
    def get_humidity():
        # Recupera los últimos 10 registros de humedad
        humidities = humidity_collection.find().sort("_id", -1).limit(10)
        result = [{"humedad": temp["humedad"], "id": str(temp["_id"])} for temp in humidities]
        return jsonify(result)
