#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>

//--------------------------------------------------------------------
// Constantes para el funcionamiento del robot

#define NUM_SERVOS 5

// Tipos de posiciones de los servos

#define DERECHO_SUP 0
#define DERECHO_INF 1
#define IZQUIERDO_SUP 2
#define IZQUIERDO_INF 3
#define DELANTERO 4

// Diferentes llamadas a recibir de raspi

#define CONNECT 0
#define GET_POS 1
#define SET_POS 2

// Estados de la conexión serie (OK o ERROR)

#define OK 0
#define ERROR 1

//--------------------------------------------------------------------
// Inicialización del controlador PCA9685

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVO_MIN 150 // Ajusta según tu servo
#define SERVO_MAX 600 // Ajusta según tu servo

//--------------------------------------------------------------------
// Clase para controlar los servos

class ServoControl {
  private:
    uint8_t servoNum;
    uint16_t angulo;
  
  public:
    ServoControl() : servoNum(255), angulo(-1) {}
    
    ServoControl(uint8_t num) {
      this->servoNum = num;
      this->angulo = -1;
    }

    void setPosition(uint16_t ang) {
      if (this->angulo == ang) return;
      uint16_t pulse = map(ang, 0, 180, SERVO_MIN, SERVO_MAX);
      pwm.setPWM(servoNum, pulse);
      this->angulo = ang;
    }

    uint16_t getPosition() {
      return this->angulo;
    }
};

//--------------------------------------------------------------------
// Declaración de los NUM_SERVOS servos

ServoControl servoControllers[NUM_SERVOS] = {
  ServoControl(DERECHO_SUP),
  ServoControl(DERECHO_INF),
  ServoControl(IZQUIERDO_SUP),
  ServoControl(IZQUIERDO_INF),
  ServoControl(DELANTERO)
};

//--------------------------------------------------------------------
// Función que a partir de un json del estilo {"0": 50, "1" : 80} setea todos los ángulos en sus servos correspondientes

void setServosPosition(const JsonObject& parametros) {
  for (JsonPair kv : parametros) {
    const char* nombreServo = kv.key().c_str();
    int nServo = atoi(nombreServo);
    uint16_t angulo = kv.value().as<uint16_t>();
    servoControllers[nServo].setPosition(angulo);
  }
}

//--------------------------------------------------------------------
// Función que devuelve un json del estilo {"0": 50, "1" : 80} con la información de todos los servos

DynamicJsonDocument getServosPosition() {
  DynamicJsonDocument root(200);
  for (int i = 0; i < NUM_SERVOS; i++) {
    root[String(i)] = servoControllers[i].getPosition();
  }
  return root;
}

//--------------------------------------------------------------------
// Función setup de arduino para iniciar la posición de los servos y el puerto serie

void setup() {
  Serial.begin(9600);

  // Iniciar la conexión I2C
  pwm.begin();
  pwm.setPWMFreq(60);  // Frecuencia de 60 Hz para los servos

  delay(1000);
}

//--------------------------------------------------------------------
// Función principal de la parte de Arduino del robot
// Lee JSON de entrada y en función del comando {"command" : (0 || 1 || 2)} (utilizando las constantes de arriba) se hace un comando u otro

void loop() {
  if (Serial.available() > 0) {
    //--------------------------------------------------------------------
    // Lectura del JSON

    String jsonStr = Serial.readStringUntil('\n');
    
    // Parsear la cadena JSON en un objeto JSON
    DynamicJsonDocument doc(200);
    DeserializationError error = deserializeJson(doc, jsonStr);
    
    if (error) {
      DynamicJsonDocument response(200);
      char serialized[128];
      response["status"] = ERROR;
      serializeJson(response, serialized);
      Serial.println(serialized);
      return;
    }

    //--------------------------------------------------------------------
    // Lectura de la comanda como entero

    int nombreCommand = doc["command"].as<int>();

    //--------------------------------------------------------------------
    // if-else para los diferentes comandos posibles (todas las funciones han sido testeadas)

    if (nombreCommand == CONNECT) {
      DynamicJsonDocument response(200);
      char serialized[128];
      response["status"] = OK;
      serializeJson(response, serialized);
      Serial.println(serialized);
      Serial.flush();
    } else if (nombreCommand == GET_POS) {
      DynamicJsonDocument servoPositions = getServosPosition();
      DynamicJsonDocument response(200);
      char serialized[128];

      response["status"] = OK;
      response["positions"] = servoPositions;

      serializeJson(response, serialized);
      Serial.println(serialized);
      Serial.flush();
    } else if (nombreCommand == SET_POS) {
      JsonObject parametros = doc["parametros"];
      setServosPosition(parametros);
      DynamicJsonDocument response(200);
      char serialized[128];
      response["status"] = OK;
      serializeJson(response, serialized);
      Serial.println(serialized);
      Serial.flush();
    } else {
      Serial.println("Error con los comandos, comando inválido");
    }
  }
}
