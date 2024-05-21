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
    MOTOR_TOPIC = os.getenv("MOTOR_TOPIC")
    MOTOR_CONTROL_TOPIC = os.getenv("MOTOR_CONTROL_TOPIC")
    HUME_TOPIC_TERRA = os.getenv("HUME_TOPIC_TERRA")
    HUME_TOPIC = os.getenv("HUME_TOPIC")
    TEMP_TOPIC = os.getenv("TEMP_TOPIC")
