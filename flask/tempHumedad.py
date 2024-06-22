#tempHumedad.py
from flask import Flask, jsonify
from mqtt_config import create_mqtt_client
import os
from db_config import get_mongo_client, get_database
from bson.objectid import ObjectId
import pytz
from settings import Config

app = Flask(__name__)

# Configuración de MongoDB
mongo_client = get_mongo_client()
db = get_database(mongo_client, 'sensor_database')
temperature_collection = db['temperatura']
humidity_collection = db['humedad']
soil_humidity_collection = db['humedad_tierra']

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(Config.TEMP_TOPIC)
    client.subscribe(Config.HUME_TOPIC)
    client.subscribe(Config.HUME_TOPIC_TERRA)

def convert_utc_to_local(utc_dt, local_tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')

def calcular_mediana_temperatura():
    temperaturas = list(temperature_collection.find().sort("_id", -1).limit(7))
    valores = [temp["temperatura"] for temp in temperaturas]
    n = len(valores)
    if n == 0:
        raise ValueError("No hay suficientes datos para calcular la mediana")
    valores.sort()
    mediana = valores[n // 2] if n % 2 != 0 else (valores[n // 2 - 1] + valores[n // 2]) / 2
    return mediana

def get_last_humedad():
    ultimo_registro = list(humidity_collection.find().sort("_id", -1).limit(1))
    if len(ultimo_registro) == 0:
        return None
    return ultimo_registro[0]["humedad"]

def get_last_7_registros(collection):
    registros = list(collection.find().sort("_id", -1).limit(7))
    return registros if len(registros) > 0 else None

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    if msg.topic == Config.TEMP_TOPIC:
        print(msg.topic + " " + payload)
        temperatura = float(payload) - 2
        #print(f'temperatura: ${temperatura}')
        if temperatura <= 0:
            try:
                temperatura = calcular_mediana_temperatura()
            except ValueError:
                print("Mediana no disponible, usando valor por defecto")
                temperatura = 18
        temperature_collection.insert_one({"temperatura": temperatura})
    elif msg.topic == Config.HUME_TOPIC:
        print(msg.topic + " " + payload)
        humedad_ajustada = float(payload) + 20
        if humedad_ajustada > 90:
            humedad_ajustada = 70
        humidity_collection.insert_one({"humedad": humedad_ajustada})
    elif msg.topic == Config.HUME_TOPIC_TERRA:
        print(msg.topic + " " + payload)
        humedad_tierra = float(payload)
        soil_humidity_collection.insert_one({"humedad_tierra": humedad_tierra})

client = create_mqtt_client(on_connect, on_message)

def setup_temperature_routes(app):
    @app.route('/temperatura')
    def get_temperature():
        local_tz = pytz.timezone("Europe/Madrid")
        try:
            mediana_temp = calcular_mediana_temperatura()
        except ValueError:
            return jsonify({"error": "No se encontraron datos suficientes"})

        ultimos_7_temperaturas = get_last_7_registros(temperature_collection)
        ultima_humedad = get_last_humedad()

        if not ultimos_7_temperaturas or ultima_humedad is None:
            return jsonify({"error": "No se encontraron datos suficientes"})

        fechas = [convert_utc_to_local(ObjectId(registro["_id"]).generation_time, local_tz) for registro in ultimos_7_temperaturas]

        result = {
            "ultimas_temperaturas": [registro["temperatura"] for registro in ultimos_7_temperaturas],
            "timestamp": fechas,
            "mediana": mediana_temp,
            "humedad": ultima_humedad,
        }
        return jsonify(result)

    @app.route('/humedad')
    def get_humidity():
        local_tz = pytz.timezone("Europe/Madrid")
        humidities = list(humidity_collection.find().sort("_id", -1).limit(10))
        result = [{
            "humedad": temp["humedad"],
            "timestamp": convert_utc_to_local(ObjectId(temp["_id"]).generation_time, local_tz)
        } for temp in humidities]
        return jsonify(result)
    
    @app.route('/humedad/tierra')
    def get_soil_humidity():
        local_tz = pytz.timezone("Europe/Madrid")
        soil_humidities = list(soil_humidity_collection.find().sort("_id", -1).limit(10))
        result = [{
            "humedad_tierra": temp["humedad_tierra"],
            "timestamp": convert_utc_to_local(ObjectId(temp["_id"]).generation_time, local_tz)
        } for temp in soil_humidities]
        return jsonify(result)
