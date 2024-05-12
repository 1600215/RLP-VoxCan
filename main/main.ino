#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>

#define PCA9685_ADDRESS 0x40
#define PWM_FREQUENCY 50

#define NUM_SERVOS 2

#define DERECHO_SUP 0
#define DERECHO_INF 1
#define IZQUIERDO_SUP 2
#define IZQUIERDO_INF 3
#define DELANTERO 4

#define CONNECT 0
#define GET_POS 1
#define SET_POS 2

#define CONNECTED 0

const int minPulse = 150;
const int maxPulse = 600;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADDRESS);

class ServoControl {
  private:
    uint8_t servoNum = NULL;
    int angulo = NULL;
  
  public:
    ServoControl() {}
    ServoControl(uint8_t num, int ang) {
      this->servoNum = num;
      this->setPosition(ang);
    }
    
    void setPosition(int ang) {
      if(this->angulo == ang) return;
      int pulse = map(ang, 0, 180, minPulse, maxPulse);
      pwm.setPWM(this->servoNum, 0, pulse);
      this->angulo = ang;
    }

    int getPosition(){ return this->angulo; }
};

ServoControl servos[NUM_SERVOS];

void setServosPosition(const JsonObject& parametros) {
  for (JsonPair kv : parametros) {

    const char* nombreServo =kv.key().c_str();
    int key = atoi(nombreServo);

    int angulo = kv.value().as<unsigned int>();
    servos[key].setPosition(angulo);
  }
}

JsonObject getServosPosition() {
  DynamicJsonDocument doc(200);
  JsonObject root = doc.to<JsonObject>();
  for (int i = 0; i < NUM_SERVOS; i++) {
    root[String(i)] = servos[i].getPosition();
  }
  return root;
}

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(PWM_FREQUENCY);


  servos[DERECHO_SUP] = ServoControl(DERECHO_SUP, 160);
  delay(10);
  servos[IZQUIERDO_SUP] = ServoControl(IZQUIERDO_SUP, 20);
  delay(10);
  
  delay(1000);
  
  servos[DERECHO_INF] = ServoControl(DERECHO_INF, 135);
  delay(10);
  servos[IZQUIERDO_INF] = ServoControl(IZQUIERDO_INF, 45);
  delay(10);
  
  
}


void loop() {
  if (Serial.available() > 0) {


    String jsonStr = Serial.readStringUntil('\n');
    
    // Parsear la cadena JSON en un objeto JSON
    DynamicJsonDocument doc(200);
    DeserializationError error = deserializeJson(doc, jsonStr);
    
    if (error) {
      Serial.println("Error al parsear JSON");
      return;
    }

    int nombreCommand = doc['command'].as<int>();

    if (nombreCommand == CONNECT) {
      DynamicJsonDocument response(200);
      char serialized[128];
      response["status"] = CONNECTED;
      serializeJson(response, serialized);
      Serial.println(serialized);

    } else if (nombreCommand == GET_POS) {
      
      JsonObject servoPositions = getServosPosition();
      char serialized[128];
      serializeJson(servoPositions, serialized);
      Serial.println(serialized);

    } else if (nombreCommand == SET_POS) {
      
      JsonObject parametros = doc["parametros"];
      setServosPosition(parametros);
    }
    else {
      
        Serial.println(nombreCommand);
    }
  }
}

