#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

//--------------------------------------------------------------------
// Configuración de la librería Adafruit PCA9685

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
#define SERVO_MIN 150  // Pulso mínimo del servo (ajusta según tu servo)
#define SERVO_MAX 600  // Pulso máximo del servo (ajusta según tu servo)

#define NUM_SERVOS 5

// Números de los servos
#define DERECHO_SUP 0
#define DERECHO_INF 1
#define IZQUIERDO_SUP 2
#define IZQUIERDO_INF 3
#define DELANTERO 4

//--------------------------------------------------------------------
// Función para mover un servo a un ángulo específico

void setServoAngle(uint8_t servoNum, uint16_t angle) {
  uint16_t pulse = map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
  pwm.writeMicroseconds(servoNum, pulse);
}

//--------------------------------------------------------------------
// Función setup de Arduino para iniciar la posición de los servos y el puerto serie

void setup() {
  Serial.begin(9600);

  // Iniciar la conexión I2C
  pwm.begin();
  pwm.setPWMFreq(60);  // Frecuencia de 60 Hz para los servos

  // Configurar la posición inicial de los servos si es necesario
  for (uint8_t i = 0; i < NUM_SERVOS; i++) {
    setServoAngle(i, 90); // Posición inicial de 90 grados
  }
}

//--------------------------------------------------------------------
// Función loop principal de Arduino para mover los servos

void loop() {
  // Mover todos los servos de 0 a 180 grados y luego de vuelta a 0
  for (uint16_t angle = 0; angle <= 180; angle += 10) {
    for (uint8_t i = 0; i < NUM_SERVOS; i++) {
      setServoAngle(i, angle);
    }
    delay(500);  // Esperar 500 ms
  }

  for (uint16_t angle = 180; angle >= 0; angle -= 10) {
    for (uint8_t i = 0; i < NUM_SERVOS; i++) {
      setServoAngle(i, angle);
    }
    delay(500);  // Esperar 500 ms
  }
}
