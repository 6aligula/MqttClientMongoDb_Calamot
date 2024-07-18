# Proyecto de Monitoreo de Humedad de la Tierra con ESP8266

## Descripción

Este proyecto utiliza una **ESP8266** para recopilar datos de humedad de la tierra, utilizando una sonda FC28. Los datos recogidos se transmiten a través de MQTT, permitiendo un monitoreo remoto y en tiempo real de las condiciones de humedad del suelo. La integración de un chip LM323 como interfaz permite la conversión de señales para su adecuada lectura y transmisión.

## Componentes

- **ESP8266**: Microcontrolador utilizado para la recolección y transmisión de datos.
- **Sonda FC28**: Sensor de humedad del suelo, utilizado para obtener lecturas precisas de la humedad.
- **Chip LM323**: Utilizado como interfaz para convertir la señal de la sonda a un voltaje adecuado para la ESP8266.
- **Divisor de Tensión**: Implementado en el pin A0 de la ESP8266 para convertir el rango de tensión de la señal de 0-3.3V a un rango de 0-1V.

## Funcionamiento

La sonda FC28 mide la humedad del suelo, generando una señal de voltaje entre 3.3V y 0V dependiendo de la humedad detectada. Esta señal es procesada por el chip LM323, que hace las veces de interfaz, para adecuarla a los requerimientos de la ESP8266. 

Para asegurar la compatibilidad con el pin A0 de la ESP8266, que solo puede leer voltajes en un rango de 0 a 1V, se utiliza un divisor de tensión. Este ajusta la señal de entrada al rango de lectura adecuado, permitiendo una lectura precisa por parte del microcontrolador.

## Comunicación

La ESP8266 transmite los datos de humedad recopilados a través de MQTT, un protocolo ligero de mensajería que permite el envío de datos a una red de dispositivos o a un servidor centralizado. Esto facilita el monitoreo remoto de las condiciones de humedad del suelo, esencial para aplicaciones como la agricultura inteligente.

Notas: 
EL Iot solo funciona con 3v ya que 5V es demasiada tensión y la variación de tensión que proporciona la sonda no es suficiente para ver el cambio en los niveles de humedad. 

