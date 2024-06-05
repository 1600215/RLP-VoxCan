#!/bin/bash

# Activar el entorno Conda
conda activate /Users/albertceballos/3curso/RLP-VoxCan/.conda

cd ../../..

# Ejecutar el servidor con nodemon
nodemon --watch server.js --exec "node /Users/albertceballos/3curso/RLP-VoxCan/webServer/server.js" &
echo "Server running"

# Ejecutar el cliente de WebSocket con múltiples conexiones con nodemon
nodemon --watch multi_client.js --exec "node /Users/albertceballos/3curso/RLP-VoxCan/raspi/test/testStandby/client.js" &
echo "Client running"
# Ejecutar el bucle funcional del robot en el entorno Conda
python /Users/albertceballos/3curso/RLP-VoxCan/raspi/test/testStandby/testStandby.py &
echo "Robot running"
# Ejecutar el generador de archivos en el entorno Conda
python /Users/albertceballos/3curso/RLP-VoxCan/raspi/test/testStandby/generateFiles.py &
echo "Files running"
# Esperar a que todos los procesos terminen
wait
