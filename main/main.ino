#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>
#include <string.h>
// Dirección del módulo PWM
#define PCA9685_ADDRESS 0x40

// Frecuencia del PWM
#define PWM_FREQUENCY 50

// Número de servos
#define NUM_SERVOS 5

#define DERECHO_SUP 0
#define DERECHO_INF 1
#define IZQUIERDO_SUP 2
#define IZQUIERDO_INF 3
#define DELANTERO 4

const int minPulse = 150;
const int maxPulse = 600;

// Inicializar el driver de servo PWM
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADDRESS);


class ServoControl {
  private:
    uint8_t servoNum;
    int angulo;
  
  public:
    ServoControl(uint8_t num, int angulo) {
      this->servoNum = num;
      setPosition(angulo);
    }
    
    void setPosition(int ang) {

      if(this->angulo == ang) return;
      int pulse = map(ang, 0, 180, minPulse, maxPulse);
      pwm.setPWM(servoNum, 0, pulse);
      this->angulo = ang;
    }

    int getPosition(){ return this.>angulo; }
};


ServoControl servos[NUM_SERVOS];



void setServosPosition(const JsonObject& parametros) {
  // Iterar sobre cada par clave-valor dentro de "parametros"
  for (JsonPair kv : parametros) {
    String nombreServo = kv.key().c_str(); // Obtener el nombre del servo
    int angulo = kv.value(); // Obtener el ángulo del servo
    servos[nombreServo].setPosition(angulo);

  }
}

JsonObject getServosPosition() {

  JsonDocument doc;
  for (int i = 0; i < NUM_SERVOS; i++) {
        doc[getServoName(i)] = servos[i].getPosition();
  }
  return doc.as<JsonObject>();
}



void setup() {
  // Iniciar la comunicación serial
  Serial.begin(9600);
  
  // Iniciar el driver de servo PWM
  pwm.begin();
  pwm.setPWMFreq(PWM_FREQUENCY);

  // Inicializar los servos
  servos[DERECHO_SUP] = ServoControl(DERECHO_SUP, 90);
  servos[DERECHO_INF] = ServoControl(DERECHO_INF, 90);
  servos[IZQUIERDO_SUP] = ServoControl(IZQUIERDO_SUP, 90);
  servos[IZQUIERDO_INF] = ServoControl(IZQUIERDO_INF, 90);
  servos[DELANTERO] = ServoControl(DELANTERO, 90);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    // Parsear el JSON
    StaticJsonDocument<200> doc;
    deserializeJson(doc, command);
    


    //Nombre de la comanda a realizar
    const String nombreCommand = doc["command"];

    //if else para ejecutar comanda
    switch (nombreCommand){

      case "CONNECT":
        JsonObject response = {
          {"status", "CONNECTED"}
        };
        serializeJson(response, Serial);
        Serial.println();
        break;

      case "getPos":

        JsonObject servoPositions = getServosPosition();
        serializeJson(servoPositions, Serial);
        Serial.println();
        break;

      case "setPos":

        JsonObject parametros = doc["parametros"];
        setServosPosition(parametros);

        break;
      default:
        break;
    }
    
  }
}
