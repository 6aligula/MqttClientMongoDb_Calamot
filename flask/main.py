# main.py
import time
from flask import Flask, jsonify, request, Response
import threading
from db_config import get_mongo_client, get_database
from mqtt_config import create_mqtt_client, publish_message
from settings import Config
from tempHumedad import setup_temperature_routes, calcular_mediana_temperatura
from flask_cors import CORS
from MotorConfig import MotorConfig

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

mongo_client = get_mongo_client()
db = get_database(mongo_client, 'motor_database')
commands_collection = db['comandos_calefaccion']
states_collection = db['estados_calefaccion']
config = MotorConfig(db)

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
        #update_motor_state(payload, command_time)
    elif topic == Config.MOTOR_CONTROL_TOPIC:
        states_collection.insert_one({
            "type": "mqtt_event",
            "state": payload,
            "time": time.time()
        })
        print(f"Estado {payload} guardado en la base de datos")

client = create_mqtt_client(on_connect, on_message)

@app.route('/')
def index():
    return "Smart Garden Calamot"

def get_motor_duration():
    config_data = db['configuracion_motor'].find_one({}, projection={'segundos': 1})
    if config_data and 'segundos' in config_data:
        return config_data['segundos']
    return 0  # Valor predeterminado en caso de que no se encuentre el documento

def get_operational_state():
    # Asegurar que se recupera el último documento de acción de control
    state_data = states_collection.find_one(
        {'type': 'control_action'},
        sort=[('_id', -1)],
        projection={'action_state': 1}
    )
    return state_data['action_state'] if state_data else None

def schedule_shutdown(milliseconds):
    seconds = milliseconds / 1000
    print(f"Scheduling shutdown in {milliseconds} milliseconds")
    time.sleep(seconds)
    if publish_message(client, Config.MOTOR_TOPIC, '0'):
        print("Motor turned off successfully.")
    else:
        print("Failed to turn off motor.")

def handle_motor_action(action, seconds, from_thread=False):
    if seconds <= 0:
        message = f"No se puede {action} el motor por 0 segundos o menos."
        if from_thread:
            print(message)
        else:
            return jsonify({"success": False, "message": message}), 400

    states_collection.insert_one({
        'type': 'control_action',
        'state': 'in_transition',  # Indicar que el motor está en transición
        'action_state': action,
        'time': time.time()
    })

    milliseconds = seconds * 1000  # Convertir segundos a milisegundos
    if action == "abrir":
        message = '1'
    elif action == "cerrar":
        message = '2'
    else:
        if from_thread:
            print("Acción inválida.")
        else:
            return jsonify({"success": False, "message": "Acción inválida."}), 400

    if publish_message(client, Config.MOTOR_TOPIC, message):
        if milliseconds > 0:
            timer = threading.Thread(target=schedule_shutdown, args=(milliseconds,))
            timer.start()
        success_message = f"{action.capitalize()} motor"
        if from_thread:
            print(success_message)
        else:
            return jsonify({"success": True, "message": success_message}), 200
    else:
        failure_message = f"Failed to {action} motor"
        if from_thread:
            print(failure_message)
        else:
            return jsonify({"success": False, "message": failure_message}), 500

def check_temperature_and_act():
    try:
        mediana = calcular_mediana_temperatura()
        print(f"Mediana de temperatura: {mediana}")
    except ValueError:
        print("No se encontraron datos suficientes")
        return

    operational_state = get_operational_state() 
    print(f"Check thread is ok, state= {operational_state}") 

    # Obtener los parámetros de la configuración de manera segura
    umbral_alto, umbral_bajo, segundos = config.get()
 
    # Lógica basada en los umbrales y el estado actual
    if mediana >= umbral_alto:
        if operational_state != 'abrir':
            handle_motor_action('abrir', segundos, from_thread=True)
    elif mediana < umbral_bajo:
        if operational_state != 'cerrar':
            print("Temperatura por debajo del umbral bajo, cerrando motor")
            handle_motor_action('cerrar', segundos, from_thread=True)
    else:
        print(f"Temperatura dentro de los umbrales alto {umbral_alto} y bajo {umbral_bajo}, no se toma acción")

def autonomous_check(interval=60):
    while True:
        check_temperature_and_act()
        time.sleep(interval)

#endpoints
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
            state = get_operational_state()
            duration = get_motor_duration()
            if state:
                print(f"Enviando estado: {state} con duración: {duration}")
                yield f"data: {{\"state\": \"{state}\", \"duration\": {duration}}}\n\n"
            else:
                print("No se encontraron datos")
                yield "data: {\"state\": \"No se encontraron datos\", \"duration\": 0}}\n\n"
            time.sleep(5)

    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/motor/autocontrol', methods=['POST'])
def auto_control_motor():
    # Asegúrate de que la solicitud contiene JSON
    if not request.is_json:
        return jsonify({"success": False, "message": "Formato de solicitud incorrecto, se espera JSON."}), 400

    data = request.get_json()
    umbral_alto = data.get('umbral_alto')
    umbral_bajo = data.get('umbral_bajo')
    segundos = data.get('segundos')

    if umbral_alto is None or umbral_bajo is None or segundos is None:
        return jsonify({"success": False, "message": "Parámetros necesarios no proporcionados."}), 400

    print(f"Configuración recibida correctamente. { umbral_alto, umbral_bajo, segundos}")
    
    # Actualizar la configuración de manera segura
    config.update(umbral_alto, umbral_bajo, segundos)
    
    # Logic to handle motor action based on temperature and thresholds
    return jsonify({"success": True, "message": "Configuración recibida correctamente."})

@app.route('/motor/get_config', methods=['GET'])
def get_config():
    umbral_alto, umbral_bajo, segundos = config.get()
    return jsonify({
        "umbral_alto": umbral_alto,
        "umbral_bajo": umbral_bajo,
        "segundos": segundos
    })

setup_temperature_routes(app)

if __name__ == '__main__':
    # Iniciar el hilo para la verificación autónoma de la temperatura
    autonomous_thread = threading.Thread(target=autonomous_check, args=(15,))  # Verificar cada 60 segundos
    autonomous_thread.daemon = True  # Permitir que el hilo se cierre al cerrar la aplicación
    autonomous_thread.start()

    app.run(debug=False, host='0.0.0.0', port=5000)