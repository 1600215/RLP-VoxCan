# VoxCan: Robot Canino Inteligente

## Que es esto?
VoxCan es un proyecto diseñado para la asignatura de Robótica en la Escuela de Ingeniería de la Universitat Autònoma de Barcelona (curso 2023-2024). Este proyecto tiene como objetivo crear un robot tipo perro con capacidades de movilidad, reconocimiento de voz, reconocimiento de objetos y comportamientos caninos realistas.

## Requirements
Estas bibliotecas son utilizadas para la manipulación y el análisis de archivos de audio.
- `audioread==3.0.1`
- `librosa==0.10.2.post1`
- `pydub==0.25.1`
- `sounddevice==0.4.7`
- `soundfile==0.12.1`
- `soxr==0.3.7`
- `SpeechRecognition==3.10.4`

Estas bibliotecas proporcionan herramientas para la manipulación de datos, el aprendizaje automático y el análisis científico.
- `joblib==1.4.2`
- `lazy_loader==0.4`
- `llvmlite==0.42.0`
- `numba==0.59.1`
- `numpy==1.26.4`
- `scikit-learn==1.4.2`
- `scipy==1.13.0`
- `threadpoolctl==3.5.0`

Bibliotecas utilizadas para manipular y analizar diferentes tipos de archivos y datos.
- `attrs==23.2.0`
- `decorator==5.1.1`
- `fpdf==1.7.2`
- `iso8601==2.1.0`
- `lxml==5.2.2`
- `msgpack==1.0.8`
- `platformdirs==4.2.2`
- `PyYAML==6.0.1`
- `unittest-xml-reporting==3.2.0`

Paquetes necesarios para la comunicación HTTP y manejo de solicitudes web.
- `aiohttp==3.9.5`
- `aiosignal==1.3.1`
- `certifi==2024.2.2`
- `charset-normalizer==3.3.2`
- `idna==3.7`
- `multidict==6.0.5`
- `requests==2.32.1`
- `urllib3==2.2.1`
- `yarl==1.9.4`

Librerias necesarias para la comunicación serie y manipulación de datos serializados.
- `cffi==1.16.0`
- `pycparser==2.22`
- `pyserial==3.5`
- `serial==0.0.97`

Otras bibliotecas necesarias para funcionalidades adicionales y optimización.
- `future==1.0.0`
- `opencv-contrib-python==4.9.0.80`
- `packaging==24.0`
- `pooch==1.8.1`
- `typing_extensions==4.11.0`

### Instalación

Para instalar todas las dependencias, ejecuta el siguiente comando:
~~~
pip install -r requirements.txt
~~~

## Documentation
Este README muestra los elementos detallados del proyecto llevado a cabo.

Cómo usar
Clonar este repositorio.
~~~
git clone https://github.com/1600215/RLP-VoxCan
~~~

Instalar las bibliotecas requeridas.

Activar python environment:
~~~
source activate venvRLP/bin/activate
~~~

Ejecutar el script de Python en cada directorio.
Agrega una Like a este repositorio si te gusta ❤.

## Descripción

El enfoque principal de este proyecto es la integración de hardware y software para lograr un funcionamiento óptimo y una interacción efectiva con el entorno. Desde la selección de componentes hasta el desarrollo de algoritmos de control, VoxCan busca proporcionar una experiencia práctica y educativa en el campo de la robótica. 
El objetivo como se ha dicho ya, es montar un robot mascota con dos patas traseras y una rueda delantera. Éste realizara unos movimientos básicos como andar, girar, sentarse, etcétera, simulando los movimientos naturales de un perro. 
Junto a ello, se ha montado un algoritmo de reconocimiento por voz para que el propio robot reconozca a su amo, o conocidos (unicamente a los integrantes del grupo). Con un webserver hemos añadido la funcionalidad de hacer las llamadas desde una interfície web, enviando audios a la Raspberry Pi y que actue como cerebro de ejecución sobre el robot.

## Reconocimiento de voz
### Algoritmo

## Módulo de movimiento
### Algoritmo

## Control de estados
### Algoritmo

## Contribución
¡Cualquier contribución es bienvenida!

## Citación
Si usas el código de este proyecto para tu trabajo académico, te animamos a citar nuestros artículos.
Si usas el código de este proyecto en la industria, también nos encantaría saber de ti; no dudes en ponerte en contacto directamente con los desarrolladores.

# Autores
- Gerard Asbert Marcos, 1603295
- Adria Martinez Muñoz, 1604086
- Albert Ceballos Aguilera, 1604259
- Raúl Quirós Morales, 1600215
