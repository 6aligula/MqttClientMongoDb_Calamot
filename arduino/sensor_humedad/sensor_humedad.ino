#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Reemplaza con tus credenciales de red WiFi
const char* ssid = "WiFi Batxillerat";
const char* password = "Calamot+";

// Dirección IP del broker MQTT
const char* mqtt_server = "192.168.1.170";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

#define SENSOR_PIN A0  // Pin donde se conecta el sensor FC-28

unsigned long previousMillis = 0;  
const long interval = 10000;       // Intervalo para actualizaciones del sensor (10 segundos)

// Valores de calibración del sensor
const int sensorMin = 0;   // Valor del sensor cuando está completamente sumergido en agua
const int sensorMax = 1023; // Valor del sensor cuando está completamente seco

void setup_wifi() {
  delay(10);
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi conectado.");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (mqttClient.connect("ESP8266Client", "admin", "lokodeldiablo")) {
      Serial.println("conectado");
    } else {
      Serial.print("falló, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" intenta de nuevo en 5 segundos");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  mqttClient.setServer(mqtt_server, 1883);
}

void loop() {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Leer el valor del sensor FC-28
    int sensorValue = analogRead(SENSOR_PIN);

    // Asegúrate de que sensorMax y sensorMin están correctamente calibrados
    float moisturePercentage = map(sensorValue, sensorMax, sensorMin, 0, 100);

    // Imprimir el valor crudo del sensor para depuración
    Serial.print("Valor crudo del sensor: ");
    Serial.println(sensorValue);

    // Imprimir el valor antes de publicarlo
    Serial.print("Publicando en el tópico 'garde/humedad/terra': ");
    Serial.println(moisturePercentage);

    // Publicar el valor de humedad
    String message = String(moisturePercentage);
    mqttClient.publish("garde/humedad/terra", message.c_str());
  }
}
