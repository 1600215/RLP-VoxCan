#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>

//--------------------------------------------------------------------
//Constantes para el funcionamieto del robot 

#define PCA9685_ADDRESS 0x40
#define PWM_FREQUENCY 50


//Numero de servos

#define NUM_SERVOS 4


//Tipos de posiciones de los servos

#define DERECHO_SUP 0
#define DERECHO_INF 1
#define IZQUIERDO_SUP 2
#define IZQUIERDO_INF 3
#define DELANTERO 4


//Diferentes llamadas a recibir de raspi

#define CONNECT 0
#define GET_POS 1
#define SET_POS 2


//Estados de la conexión serie (OK o ERROR)

#define OK 0
#define ERROR 1


// constantes para calcular posiciones de un servo

const int minPulse = 150;
const int maxPulse = 600;


//--------------------------------------------------------------------
//Inicialización del ServoDriver que nos permitirá modificar nuestros servos

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(PCA9685_ADDRESS);


//--------------------------------------------------------------------
//Clase para controlar los servos 

class ServoControl {
  private:
    uint8_t servoNum= NULL;
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


//--------------------------------------------------------------------
//Declaración de los NUM_SERVOS servos

ServoControl servos[NUM_SERVOS];


//--------------------------------------------------------------------
//función que a partir de un json del estilo {"0": 50, "1" : 80} setea todos los angulos en sus servos correspondientes

void setServosPosition(const JsonObject& parametros) {
  for (JsonPair kv : parametros) {
    const char* nombreServo =kv.key().c_str();
    int nServo = atoi(nombreServo);
    int angulo = kv.value().as<unsigned int>();
    servos[nServo].setPosition(angulo);
  }
}

//--------------------------------------------------------------------
//Función que devuelve un json del estilo {"0": 50, "1" : 80} con la información de todos los servos

DynamicJsonDocument getServosPosition() {
  DynamicJsonDocument root(200);
  for (int i = 0; i < NUM_SERVOS; i++) {
    root[String(i)] = servos[i].getPosition();
  }
  return root;
}


//--------------------------------------------------------------------
//Función setup de arduino para iniciar la posición de los servos y el puerto serie

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(PWM_FREQUENCY);
  servos[DERECHO_SUP] = ServoControl(DERECHO_SUP, 110);
  delay(20);

  servos[IZQUIERDO_SUP] = ServoControl(IZQUIERDO_SUP, 50);
  delay(2000);

  servos[DERECHO_INF] = ServoControl(DERECHO_INF, 130);
  delay(20);

  servos[IZQUIERDO_INF] = ServoControl(IZQUIERDO_INF, 70);
  delay(20);
}

//--------------------------------------------------------------------
//Función principal de la parte de arduino del robot
//Lee json de entrada y en función del comando {"command" : (0 || 1 || 2)} (utilizando las constantes de arriba) se hace un comando o otro 

void loop() {
  if (Serial.available() > 0) {


    //--------------------------------------------------------------------
    //Lectura del json

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
      return 0;
    }


    //--------------------------------------------------------------------
    //Lectura de la comanda como entero

    int nombreCommand = doc["command"].as<int>();

    //--------------------------------------------------------------------
    //if-else para los diferentes comandos possibles (todas las funciones han sido testeadas)

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

    }
    else {

        Serial.println("Error con los comandos, comando invalido");
        return 0;
    }
  }
}

