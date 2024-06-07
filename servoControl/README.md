

# Control de Servos con Arduino y Raspberry Pi

Esta parte del proyecto permite controlar 5 servos conectados a un Arduino mediante comandos enviados desde una Raspberry Pi a través de una conexión serie. Los servos pueden recibir comandos para posicionarse en ángulos específicos y se puede obtener su estado actual.

## Estructura del Proyecto

```plaintext
└───ServoControl/
    ├───src/
    │   └───ServoControl.ino
    └───README.md
```

## Librerías Requeridas

- [Servo.h](https://www.arduino.cc/en/Reference/Servo): Librería estándar para controlar servos.
- [ArduinoJson.h](https://arduinojson.org/): Librería para manipular JSON en Arduino.

## Instalación y Configuración

### 1. Conexión del Hardware

1. Conecta los 5 servos a los pines especificados en el código de Arduino.
   - Derecho Superior: Pin 3
   - Izquierdo Superior: Pin 5
   - Derecho Inferior: Pin 6
   - Izquierdo Inferior: Pin 9
   - Delantero: Pin 10

2. Conecta el Arduino a la Raspberry Pi mediante un cable USB.

### 2. Configuración del Arduino

1. Descarga e instala las librerías requeridas desde el Administrador de Librerías del IDE de Arduino.
2. Sube el script `ServoControl.ino` al Arduino.

### 3. Configuración de la Raspberry Pi

Asegúrate de tener configurada la comunicación serie en la Raspberry Pi y de que esté lista para enviar y recibir datos desde el Arduino.

Veáse en la parte del proyecto `/raspi`.

## Uso

### Comandos Disponibles

- **CONNECT (0):** Verifica la conexión con el Arduino.
- **GET_POS (1):** Obtiene las posiciones actuales de todos los servos.
- **SET_POS (2):** Establece nuevas posiciones para los servos mediante un JSON con los parámetros correspondientes.

### Ejemplo de JSON para SET_POS

```json
{
  "command": 2,
  "parametros": {
    "0": 50,
    "1": 80,
    "2": 120,
    "3": 90,
    "4": 60
  }
}
```

## Código

### Inicialización de los Servos

El código inicializa 5 servos, cada uno vinculado a un pin específico del Arduino.

```cpp
Servo servos[NUM_SERVOS];
servos[DERECHO_SUP].attach(3);
servos[IZQUIERDO_SUP].attach(5);
servos[DERECHO_INF].attach(6);
servos[IZQUIERDO_INF].attach(9);
servos[DELANTERO].attach(10);
```

### Control de los Servos

La clase `ServoControl` permite controlar la posición de cada servo y mantener el estado actual del ángulo.

```cpp
class ServoControl {
  private:
    uint8_t servoNum;
    int angulo;
    Servo* servo;
  
  public:
    ServoControl() : servoNum(255), angulo(-1), servo(nullptr) {}
    
    ServoControl(uint8_t num, Servo* srv) {
      this->servoNum = num;
      this->servo = srv;
      this->angulo = -1;
    }
    
    void setPosition(int ang) {
      if (this->angulo == ang) return;
      servo->write(ang);
      this->angulo = ang;
    }

    int getPosition() {
      return this->angulo;
    }
};
```

### Funciones Principales

- **setServosPosition:** Establece las posiciones de los servos a partir de un objeto JSON.
- **getServosPosition:** Devuelve un objeto JSON con las posiciones actuales de los servos.
- **setup:** Configura la comunicación serie y los servos.
- **loop:** Procesa los comandos recibidos a través de la conexión serie.

