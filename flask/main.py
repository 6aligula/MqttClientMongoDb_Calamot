# main.py
import time
from flask import Flask, jsonify, request, Response
import threading
from db_config import get_mongo_client, get_database
from mqtt_config import create_mqtt_client, publish_message
from settings import Config
from tempHumedad import setup_temperature_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

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
        command_time = time.time()  # Obtener el tiempo actual
        commands_collection.insert_one({"action": payload, "time": command_time})
        print(f"Comando {payload} guardado en la base de datos con tiempo {command_time}")
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

def handle_motor_action(action, seconds):
    if seconds <= 0:
        return jsonify({"success": False, "message": f"No se puede {action} el motor por 0 segundos o menos."}), 400

    milliseconds = seconds * 1000  # Convertir segundos a milisegundos
    if action == "abrir":
        message = '1'
    elif action == "cerrar":
        message = '2'
    else:
        return jsonify({"success": False, "message": "Acción inválida."}), 400

    if publish_message(client, Config.MOTOR_TOPIC, message):
        if milliseconds > 0:
            timer = threading.Thread(target=schedule_shutdown, args=(milliseconds,))
            timer.start()
        return jsonify({"success": True, "message": f"{action}"}), 200
    else:
        return jsonify({"success": False, "message": f"Failed to {action} motor"}), 500

@app.route('/motor/abrir', methods=['POST'])
def abrir_motor():
    seconds = request.args.get('seconds', default=0, type=int)
    return handle_motor_action("abrir", seconds)

@app.route('/motor/cerrar', methods=['POST'])
def cerrar_motor():
    seconds = request.args.get('seconds', default=0, type=int)
    return handle_motor_action("cerrar", seconds)

@app.route('/motor/estado', methods=['GET'])
def get_last_state():
    last_state = list(states_collection.find().sort('_id', -1).limit(1))
    if len(last_state) > 0:
        return jsonify({"state": last_state[0]['state']})
    else:
        return jsonify({"error": "No se encontraron datos"}), 404

@app.route('/motor/events', methods=['GET'])
def motor_events():
    def event_stream():
        while True:
            last_state = list(states_collection.find().sort('_id', -1).limit(1))
            if last_state:
                state = last_state[0]['state']
                last_command = list(commands_collection.find().sort('_id', -1).limit(1))
                if last_command:
                    command_time = last_command[0].get('time', 'No time data')
                else:
                    command_time = 'No time data'
                print(f"Enviando estado: {state} con tiempo: {command_time}")
                yield f"data: {{\"state\": \"{state}\", \"time\": \"{command_time}\"}}\n\n"
            else:
                print("No se encontraron datos")
                yield "data: {\"state\": \"No se encontraron datos\", \"time\": \"No se encontraron datos\"}\n\n"
            time.sleep(5)

    return Response(event_stream(), mimetype='text/event-stream')


setup_temperature_routes(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
