# mqtt_config.py
import paho.mqtt.client as mqtt
from settings import Config

def create_mqtt_client(on_connect, on_message):
    client = mqtt.Client()
    try:
        if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
            print("Connecting with username and password")
            client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)

        print(f"Attempting to connect to MQTT broker at {Config.MQTT_BROKER}")
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(Config.MQTT_BROKER, 1883, 60)
        client.loop_start()
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
    return client


def publish_message(client, topic, message):
    try:
        result = client.publish(topic, message)
        if result.rc == 0:
            print(f"Message published to {topic}")
            return True
        else:
            print(f"Failed to publish message: {mqtt.error_string(result.rc)}")
            return False
    except Exception as e:
        print(f"Exception while publishing message: {e}")
        return False
