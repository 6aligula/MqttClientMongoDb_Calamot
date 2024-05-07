# /flask/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    MONGO_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGODB_PORT", "27017")
    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    ACTIVAR_TOPIC = os.getenv("ACTIVAR_TOPIC")
    DESACTIVAR_TOPIC = os.getenv("DESACTIVAR_TOPIC")
