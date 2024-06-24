### Test de toda la maquina de estados que interactua entre el servidor web y el robot 

Simula el bucle funcional del robot, leyendo archivos subidos por los clientes y procesa para saer si hay un comando o no.
Caso de haber comando cambia de estado, sino sigue analizando archivos

### Instalación

`npm install` o `pnpm install` instalará todos los paquetes necesarios para el servidor y el cliente.

### Test general

Test en tiempo real, a partir de server.js, generar archivos que se analizarán por el bucle funcional del robot realizando cambios de estado.

1. `node server/server.js` - Servidor
2. `python test/testLoop.py` - Bucle funcional robot 

### Tests unitarios

1. `python test/testRecognizeAudio.py` - Analiza toda la carpeta uploads/ y devuevle el texto de cada audio.
2. `python test/testPredict.py` - Analiza toda la carpeta uploads/ y devuelve el identificador de cada clase persona que es.

### Test Real 

Simula todo el bucle funcional con el movimiento implementado.

1. `node server/server.js` - Servidor
2. `python test/testAll.py` - Bucle funcional robot, con movimiento
