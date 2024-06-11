#main.py
import time
from flask import Flask, jsonify, request
import threading
from db_config import get_mongo_client, get_database
from mqtt_config import create_mqtt_client, publish_message
from settings import Config
from tempHumedad import setup_temperature_routes

app = Flask(__name__)

mongo_client = get_mongo_client()
db = get_database(mongo_client, 'motor_database')
commands_collection = db['comandos_calefaccion']
states_collection = db['estados_calefaccion']

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(Config.MOTOR_TOPIC)
    client.subscribe(Config.MOTOR_CONTROL_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    topic = msg.topic
    print(f"Message received on topic {msg.topic}: {payload}")
    if topic == Config.MOTOR_TOPIC:
        commands_collection.insert_one({"action": payload})
        print(f"Comando {payload} guardado en la base de datos")
    elif topic == Config.MOTOR_CONTROL_TOPIC:
        states_collection.insert_one({"state": payload})
        print(f"Estado {payload} guardado en la base de datos")

client = create_mqtt_client(on_connect, on_message)

@app.route('/')
def index():
    return "MQTT to Flask Bridge"

def schedule_shutdown(milliseconds):
    seconds = milliseconds / 1000
    print(f"Scheduling shutdown in {milliseconds} milliseconds")
    time.sleep(seconds)
    if publish_message(client, Config.MOTOR_TOPIC, '0'):
        print("Motor turned off successfully.")
    else:
        print("Failed to turn off motor.")

@app.route('/motor/encender', methods=['POST'])
def encender_motor():
    seconds = request.args.get('seconds', default=0, type=int)
    if seconds <= 0:
        return jsonify({"success": False, "message": "No se puede encender el motor por 0 segundos o menos."}), 400

    milliseconds = seconds * 200
    if publish_message(client, Config.MOTOR_TOPIC, '1'):
        if milliseconds > 0:
            timer = threading.Thread(target=schedule_shutdown, args=(milliseconds,))
            timer.start()
        return jsonify({"success": True, "message": "Motorizando...", "shutdown_in": f"{milliseconds} milliseconds"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to turn on dispenser"}), 500

@app.route('/motor/apagar', methods=['POST'])
def apagar_motor():
    try:
        client.publish(Config.MOTOR_TOPIC, '0')
        return jsonify({"success": True, "message": "Motor apagado"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/motor/estado', methods=['GET'])
def get_last_state():
    if states_collection.count_documents({}) > 0:
        last_state = states_collection.find().sort('_id', -1).limit(1)
        return jsonify({"state": list(last_state)[0]['state']})
    else:
        return jsonify({"error": "No se encontraron datos"}), 404

setup_temperature_routes(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
