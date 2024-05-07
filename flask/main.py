#main.py
import time
from flask import Flask, jsonify, request
import threading
from db_config import get_mongo_client, get_database
from mqtt_config import create_mqtt_client, publish_message
from settings import Config

app = Flask(__name__)

mongo_client = get_mongo_client()
db = get_database(mongo_client, 'motor_database')
activar_collection = db['activar']
desactivar_collection = db['desactivar']

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if rc == 0:
        client.subscribe(Config.ACTIVAR_TOPIC)
        client.subscribe(Config.DESACTIVAR_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    collection = activar_collection if msg.topic == Config.ACTIVAR_TOPIC else desactivar_collection
    try:
        collection.insert_one({msg.topic: int(payload)})
    except Exception as e:
        print(f"Failed to insert data: {e}")
        
client = create_mqtt_client(on_connect, on_message)
client.loop_start()

@app.route('/')
def index():
    return "MQTT to Flask Bridge"


def schedule_shutdown(milliseconds):
    seconds = milliseconds / 1000  # Convertir milisegundos a segundos
    print(f"Scheduling shutdown in {milliseconds} milliseconds")
    time.sleep(seconds)  # time.sleep espera segundos, por lo que convertimos los milisegundos a segundos.
    if publish_message(client, Config.ACTIVAR_TOPIC, '0'):
        print("Motor turned off successfully.")
    else:
        print("Failed to turn off motor.")

@app.route('/motor/encender', methods=['POST'])
def encender_motor():
    seconds = request.args.get('seconds', default=0, type=int)  # Obtener segundos del parámetro de consulta
    
    if seconds <= 0:
        return jsonify({"success": False, "message": "No se puede encender el motor por 0 segundos o menos."}), 400
    
    milliseconds = seconds * 200  # Convertir segundos a milisegundos (1 segundo = 100 milisegundos)
    if publish_message(client, Config.ACTIVAR_TOPIC, '1'):
        if milliseconds > 0:
            # Programa un hilo para apagar el dispensador después del tiempo especificado en milisegundos
            timer = threading.Thread(target=schedule_shutdown, args=(milliseconds,))
            timer.start()
        return jsonify({"success": True, "message": "Motorizando...", "shutdown_in": f"{milliseconds} milliseconds"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to turn on dispenser"}), 500


@app.route('/motor/apagar', methods=['POST'])
def apagar_motor():
    try:
        client.publish(Config.ACTIVAR_TOPIC, '0')
        return jsonify({"success": True, "message": "Motor apagado"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')