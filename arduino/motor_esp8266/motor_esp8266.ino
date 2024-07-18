#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//Información de nuestro WIFI
const char* ssid = "WiFi Batxillerat";
const char* password = "Calamot+";
const char* mqtt_server = "192.168.1.170";

WiFiClient espClient;//Creamos un objeto de la clase cliente wifi
PubSubClient client(espClient);//
//definimos el pin 0 como controlador del rele
int motorPin = 5; // Pin D1 en ESP8266
int motorPin2 = 4; // Pin D2 en ESP8266

//Funcion para conectarnos a la red wifi
void setup_wifi() {

  delay(10);
  // Empezamos a conectar con el router de casa
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  //Mientras se esta conectando estamos imprimiendo puntos en la salida serial
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  //iniciar semilla para la funcion ramdom
  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void startTimer() {
  delay(20000); // Esperar 20 segundos
  digitalWrite(motorPin, HIGH);  // Apagar ambos relés
  digitalWrite(motorPin2, HIGH);
  client.publish("garden/motor/control", "7"); // Notificar que ambos relés están apagados
}

//Funcion que se ejecuta cuando recibimos el mensaje
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.print("] ");
  //Mediante el bucle for mostramos por pantalla los mensajes contenidos en la variable payload
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if ((char)payload[0] == '1') {
      digitalWrite(motorPin, LOW);   // Activamos el primer relé
      digitalWrite(motorPin2, HIGH); // Apagamos el segundo relé
      client.publish("garden/motor/control", "1");
      //startTimer(); // Iniciar el temporizador de 20 segundos
  } else if ((char)payload[0] == '2') {
      digitalWrite(motorPin, HIGH);  // Apagamos el primer relé
      digitalWrite(motorPin2, LOW);  // Activamos el segundo relé
      client.publish("garden/motor/control", "2");
      //startTimer(); // Iniciar el temporizador de 20 segundos
  } else {
      digitalWrite(motorPin, HIGH);  // Apagamos ambos relés
      digitalWrite(motorPin2, HIGH); // Apagamos ambos relés
      client.publish("garden/motor/control", "0");
  }

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    //(client.connect(clientId.c_str(), "admin", "lokodeldiablo"))
    if (client.connect(clientId.c_str(), "admin", "lokodeldiablo")) {
      Serial.println("connected");
      // Once connected, publicar mensajes
      client.publish("garden/motor/control", "0");
      // ... and resubscribe en el topic casa/caldera(la raspberry enviara las ordenes)
      client.subscribe("garden/motor");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
//Primera funcion a ejecutarse en el programa
void setup() {
  pinMode(motorPin, OUTPUT);  //Programar pin como salida
  pinMode(motorPin2, OUTPUT);
  digitalWrite(motorPin, HIGH);  //Ponemos la salida del pin en alto para que el motor este en OFF al principio
  digitalWrite(motorPin2, HIGH);
  Serial.begin(115200);// Configurar velocidad de comunicacion en bites por segundo 
  setup_wifi(); //Llama a la funcion para poner en marcha el cliente wifi
  client.setServer(mqtt_server, 1883);//Configurar el servidor mqtt_server al cual se conectara el cliente por el puerto 1883
  client.setCallback(callback);//Llamar a la funcion callback para procesar las ordenes del broker
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
