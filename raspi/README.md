## Estructura del Programa

### Estados de la máquina de estados del Robot (`main.py`)

- **Estados del Robot**:
  - `CONNECT`: Conexión con el Arduino Nano.
  - `SET_INIT`: Configuración inicial de la posición del robot.
  - `CALIBRATION`: Calibración de servos del robot.
  - `STANDBY`: Espera de comandos de voz.
  - `SIT`, `STANDUP`, `WALK`, `ROTATE`: Ejecuta las acciones correspondientes a los comandos de voz.

## Flujo del Programa

1. **Inicio del Bucle Principal**:
   - Se inicializa el hardware necesario (LEDs, puerto serie, MPU6050).
   - Se establece la conexión con el Arduino Nano.

2. **Calibración y Posición Inicial**:
   - Se configuran las posiciones iniciales y se calibran los servos del robot.

3. **Espera y Procesamiento de Comandos de Voz**:
   - El programa entra en estado `STANDBY` y espera comandos de voz.
   - Cuando se detecta un nuevo archivo de audio, se procesa para extraer el comando de voz.
   - Dependiendo del comando, se transita a un nuevo estado (`SIT`, `STANDUP`, `WALK`, `ROTATE`).

4. **Ejecución de Acciones Basadas en Estados**:
   - Cada estado del robot tiene su propio conjunto de acciones que se ejecutan hasta recibir un nuevo comando de voz.

### Módulo de Audio (`modules.audio`)

- **Detección de Archivos de Audio**: Detecta nuevos archivos WAV subidos por diferentes clientes.
- **Procesamiento de Audio**: Convierte el archivo a formato WAV si es necesario, predice la identidad de la persona en el audio, y reconoce el texto usando Google Speech Recognition.
- **Comandos de Voz**: Extrae y ejecuta comandos de voz reconocidos para cambiar el estado del robot (e.g., "siéntate", "ven aquí", "gira").
- **Manejo de Estados**: Dependiendo del texto reconocido y del estado actual, transita entre diferentes estados (`STANDBY`, `WALK`, `SIT`, `STANDUP`, `ROTATE`).
- **Interacción con el Servidor Web**: Notifica al servidor web el inicio y fin de procesamiento de comandos.


### Módulo Motion

- **Cinemática inversa y directa del robot**: A partir de un estudio previmente hecho se crea una matriz de transformaciones del robot que implementa tanto cinematica inversa y directa del robot.

- **Mapeado de angulos (esquema -> servos) & (servos -> esquema)**: Funciones necesarias para implementar la conversión de los angulos del esquema con los angulos de los servos.

- **Movimiento, funciones que realizan los estados de la máquina de estados del robot**: Implementación de las funcioes de WALK, SIT, 
STANDUP, ROTATE.

### Módulo Calibrate

- **Calibración del robot**: Algoritmo que recorre una serie de angulos despalazados al original para intentar poner el robot lo más equilibrado posible.

### Módulo Web

- **Comunicación con servidor web**:Funciones que mandan peticiones al servidor web de la web que controla el robot.

### Módulo arduino

- **Comunicación Arduino - Raspi**:La raspberry pi y el arduino están conectados mediante el puerto serie, a partir del protocolo de comunicación establecido con JSONs, se enviarán comandos y se recibirán datos.
