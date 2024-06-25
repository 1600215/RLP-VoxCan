# Proyecto de Interacción con Archivos de Audio

Este proyecto permite a un cliente subir archivos de audio a un servidor, que luego son procesados por un robot para realizar comandos específicos basados en el reconocimiento de voz. El sistema utiliza Express para el servidor, Socket.io para la comunicación en tiempo real y múltiples módulos para el procesamiento de audio y la interacción con el robot.
La web, solo permite la comunicación entre clientes via Socket.io y la subida de archivos a una carpeta, el procesamiento de audio se hace desde el estado STANDBY del robot.

## Contenido

- [Descripción General](#descripción-general)
- [Estructura del servidor](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración del Servidor](#configuración-del-servidor)
- [Configuración del Cliente](#configuración-del-cliente)
- [Ejecutar el Proyecto](#ejecutar-el-proyecto)

## Descripción General

El proyecto consta de dos componentes principales:

1. **Servidor**: Implementado con Express y Socket.io, gestiona la subida de archivos de audio y la comunicación en tiempo real con el cliente.
2. **Cliente**: Una interfaz web que permite al usuario grabar y subir archivos de audio al servidor.

## Estructura del Proyecto

```plaintext
webServer/
├── certs/
│   ├── cert.pem
│   ├── csr.pem
│   └── key.pem
├── public/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── uploads/
├── README.md
├── package.json
└── server.js
```

## Requisitos 

- Node.js
- npm o pnpm

## Configuración del Servidor

1. Instala las dependencias:

    `npm install` o `pnpm install`

3. Genera los certificados SSL y colócalos en el directorio `certs`.

    1. `openssl genrsa -out key.pem 2048`
    2. `openssl req -new -key key.pem -out csr.pem`
    3. `openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem`

4. Ejecuta el servidor:

    `node server.js`

## Configuración del Cliente

A partir de la url del servidor con el metodo GET podemos acceder a la parte del cliente.
Se puede acceder con otros dispositivos conectandolos en la misma red local y dando a conocer la ip dentro de la red local, así se podrà aprovechar la funcionalidad de Socket.io.

## Configuración del Servidor

Asegurate de tener el puerto 3000 disponible, sino cambia de puerto.

## Ejecutar el Proyecto

Como hemos dicho antes `node server.js`.
Tanto cliente como servidor están gestionados desde server.js.

- Punto importante: 

La url debe de ser https://... para poder utilizar la api de mediaDevices y intercambiar media data.

