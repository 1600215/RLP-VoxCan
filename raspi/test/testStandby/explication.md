### Test del estado standby comunicado con el servidor creado en express con node js

## 1. Client.js 

Define todo lo que es el cliente para simular 4 clientes subiendo archivos en bucle

## 2. testStandby.py 

Simula el bucle funcional del robot, leyendo archivos subidos por los clientes y procesa para saer si hay un comando o no.
Caso de haber comando cambia de estado, sino sigue analizando archivos

### Para testear

Ejecutar tanto server.js como client.js y testStandby.py

Para ser más realistas unicamente testStanby.py y server.js.
