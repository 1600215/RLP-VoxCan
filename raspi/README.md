## Estructura del Programa

### Módulo de Audio (`modules.audio`)

- **Detección de Archivos de Audio**: Detecta nuevos archivos WAV subidos por diferentes clientes.
- **Procesamiento de Audio**: Convierte el archivo a formato WAV si es necesario, predice la identidad de la persona en el audio, y reconoce el texto usando Google Speech Recognition.
- **Comandos de Voz**: Extrae y ejecuta comandos de voz reconocidos para cambiar el estado del robot (e.g., "siéntate", "ven aquí", "gira").
- **Manejo de Estados**: Dependiendo del texto reconocido y del estado actual, transita entre diferentes estados (`STANDBY`, `WALK`, `SIT`, `STANDUP`, `ROTATE`).
- **Interacción con el Servidor Web**: Notifica al servidor web el inicio y fin de procesamiento de comandos.

### Bucle Principal del Robot (`main.py`)

- **Inicialización de Hardware**: Configura GPIO para LEDs, inicializa el puerto serie para comunicación con un Arduino Nano, e inicializa un sensor MPU6050.
- **Gestión de Estados**: Mantiene un bucle continuo que monitoriza y actualiza el estado del robot basado en los comandos de voz procesados.
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

## Interacciones Clave

- **Usuario**: Sube archivos de audio con comandos de voz.
- **Módulo de Audio**: Procesa los archivos de audio, reconoce el texto y determina los comandos.
- **Bucle Principal**: Controla el estado del robot y ejecuta acciones basadas en los comandos de voz.
- **Servidor Web**: Interactúa con el módulo de audio para indicar el inicio y fin del procesamiento de comandos.

## Estado del Robot

Los estados del robot controlan las acciones específicas que realiza. Los estados clave incluyen:

- `STANDBY`: El robot está en espera y listo para recibir nuevos comandos.
- `WALK`: El robot camina hacia una dirección específica.
- `SIT`: El robot se sienta.
- `STANDUP`: El robot se levanta de una posición sentada.
- `ROTATE`: El robot gira a un ángulo específico basado en el comando de voz.


## Instalación y Ejecución

### Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecución

```bash
python main.py
```
