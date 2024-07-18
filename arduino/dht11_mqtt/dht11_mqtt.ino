// Import required libraries
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Adafruit_Sensor.h>
#include <PubSubClient.h>
#include <DHT.h>

// Reemplaza con tus credenciales de red WiFi
const char* mqtt_server = "192.168.1.170";
const char* ssid = "WiFi Batxillerat";
const char* password = "Calamot+";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

#define DHTPIN 5          // Pin D1 en ESP8266
#define DHTTYPE DHT11     // DHT 11
DHT dht(DHTPIN, DHTTYPE);

unsigned long previousMillis = 0;  // Almacenará la última vez que se actualizó el DHT
const long interval = 10000;       // Intervalo para actualizaciones DHT (10 segundos)

void setup_wifi() {
  delay(10);
  // Conectarse a la red WiFi
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
  // Bucle hasta que estemos reconectados
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
  dht.begin();
}

void loop() {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Lee la temperatura como Celsius (el valor predeterminado)
    float newT = dht.readTemperature();
    // Lee la humedad
    float newH = dht.readHumidity();

    if (!isnan(newT) && !isnan(newH)) {
      String createdBy = "Hector";
      String message = String(newT) + "-" + String(newH) + "-" + String(createdBy);
      String temp = String(newT);
      String hume = String(newH);
      // Publica los valores de temperatura y humedad
      mqttClient.publish("garden/temperatura", temp.c_str());
      mqttClient.publish("garden/humedad", hume.c_str());
      
      Serial.print("Temperatura: ");
      Serial.print(newT);
      Serial.print("C, Humedad: ");
      Serial.print(newH);
      Serial.println("%");
      
    } else {
      Serial.println("Error al leer del sensor DHT");
    }
  }
}