# main.py
import time
from flask import Flask, jsonify, request, Response
import threading
from db_config import get_mongo_client, get_database
from mqtt_config import create_mqtt_client, publish_message
from settings import Config
from tempHumedad import setup_temperature_routes, calcular_mediana_temperatura
from flask_cors import CORS
from flask_socketio import SocketIO
import eventlet
from MotorConfig import MotorConfig
import logging
from logging.handlers import RotatingFileHandler

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)  # Cambia a logging.DEBUG para más detalles si es necesario

# Configuración del handler para guardar los logs en un archivo, con rotación automática
handler = RotatingFileHandler('/app/logs/app.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Agregar el handler al logger principal
logging.getLogger().addHandler(handler)

app = Flask(__name__)
# Para uso en Flask
app.logger.addHandler(handler)

CORS(app)  # Habilitar CORS para toda la aplicación
eventlet.monkey_patch()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

mongo_client = get_mongo_client()
db = get_database(mongo_client, 'motor_database')
commands_collection = db['comandos_calefaccion']
states_collection = db['estados_calefaccion']
config = MotorConfig(db)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    client.subscribe(Config.MOTOR_TOPIC)
    client.subscribe(Config.MOTOR_CONTROL_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    topic = msg.topic
    logging.info(f"Message received on topic {msg.topic}: {payload}")
    if topic == Config.MOTOR_TOPIC:
        command_time = time.time()  # Obtener el tiempo actual
        commands_collection.insert_one({"action": payload, "time": command_time})
        logging.info(f"Comando {payload} guardado en la base de datos con tiempo {command_time}")
        #update_motor_state(payload, command_time)
    elif topic == Config.MOTOR_CONTROL_TOPIC:
        states_collection.insert_one({
            "type": "mqtt_event",
            "state": payload,
            "time": time.time()
        })
        logging.info(f"Estado {payload} guardado en la base de datos")

client = create_mqtt_client(on_connect, on_message)

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

# Función para emitir el estado del motor
def emit_motor_state(state, duration):
    if not state or duration is None:
        state = 'error'
        duration = 1
    socketio.emit('motor_state', {'state': state, 'duration': duration})


@app.route('/')
def index():
    return "Smart Garden Calamot"

def get_motor_duration():
    config_data = db['configuracion_motor'].find_one({}, projection={'segundos': 1})
    if config_data and 'segundos' in config_data:
        return config_data['segundos']
    return 10  # Valor predeterminado en caso de que no se encuentre el documento

def get_operational_state():
    # Asegurar que se recupera el último documento de acción de control
    state_data = states_collection.find_one(
        {'type': 'control_action'},
        sort=[('_id', -1)],
        projection={'action_state': 1}
    )
    return state_data['action_state'] if state_data else 'cerrar'

def schedule_shutdown(milliseconds):
    seconds = milliseconds / 1000
    logging.info(f"Scheduling shutdown in {milliseconds} milliseconds")
    time.sleep(seconds)
    if publish_message(client, Config.MOTOR_TOPIC, '0'):
        logging.info("Motor turned off successfully.")
    else:
        logging.info("Failed to turn off motor.")

def handle_motor_action(action, seconds, from_thread=False):
    if seconds <= 0:
        message = f"No se puede {action} el motor por 0 segundos o menos."
        if from_thread:
            logging.error(message)
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
            logging.error("Acción inválida.")
        else:
            return jsonify({"success": False, "message": "Acción inválida."}), 400

    if publish_message(client, Config.MOTOR_TOPIC, message):
        if milliseconds > 0:
            timer = threading.Thread(target=schedule_shutdown, args=(milliseconds,))
            timer.start()
        success_message = f"{action.capitalize()} motor"
        emit_motor_state(action, seconds)  # Emitir estado del motor
        if from_thread:
            logging.info(success_message)
        else:
            return jsonify({"success": True, "message": success_message}), 200
    else:
        failure_message = f"Failed to {action} motor"
        if from_thread:
            logging.error(failure_message)
        else:
            return jsonify({"success": False, "message": failure_message}), 500

def check_temperature_and_act():
    try:
        mediana = calcular_mediana_temperatura()
        logging.info(f"Mediana de temperatura: {mediana}")
    except ValueError:
        logging.error("No se encontraron datos suficientes para calcular la mediana.")
        return

    operational_state = get_operational_state() 
    logging.info(f"Check thread is ok, state= {operational_state}") 

    # Obtener los parámetros de la configuración de manera segura
    umbral_alto, umbral_bajo, segundos = config.get()
 
    # Lógica basada en los umbrales y el estado actual
    if mediana >= umbral_alto:
        if operational_state != 'abrir':
            handle_motor_action('abrir', segundos, from_thread=True)
    elif mediana < umbral_bajo:
        if operational_state != 'cerrar':
            logging.info("Temperatura por debajo del umbral bajo, cerrando motor")
            handle_motor_action('cerrar', segundos, from_thread=True)
    else:
        logging.info(f"Temperatura dentro de los umbrales alto {umbral_alto} y bajo {umbral_bajo}, no se toma acción")

def autonomous_check(interval=60):
    logging.info("Iniciando verificación de temperatura.")
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
    state = get_operational_state()
    duration = get_motor_duration()
    if state:
        logging.info(f"Enviando estado: {state} con duración: {duration}")
        return jsonify({"state": state, "duration": duration})
    else:
        logging.error("No se encontraron datos")
        return Response({"state": "no hay datos", "duration": "0"})

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

    logging.info(f"Configuración recibida correctamente. { umbral_alto, umbral_bajo, segundos}")
    
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

def start_autonomous_check():
    logging.info("Iniciando la aplicación Flask")
    # Iniciar el hilo para la verificación autónoma de la temperatura
    autonomous_thread = threading.Thread(target=autonomous_check, args=(15,))  # Verificar cada 15 segundos
    autonomous_thread.daemon = True  # Permitir que el hilo se cierre al cerrar la aplicación
    logging.info("Iniciando el hilo de verificación autónoma")
    autonomous_thread.start()

setup_temperature_routes(app)
# Llama a la función cuando se importa el módulo
start_autonomous_check()

if __name__ == '__main__':
    pass
    #socketio.run(app, host='0.0.0.0', port=5002)
