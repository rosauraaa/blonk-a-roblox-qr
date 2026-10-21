# Bonk-a-Blox: un minijuego de Realidad Aumentada que vive dentro de un código QR

*(Borrador para LinkedIn · ~390 palabras. Antes de publicar, agrega el video o GIF y revisa los enlaces.)*

**Objetivo.** En la materia de Realidad Virtual y Aumentada el reto fue crear una experiencia de RA para el celular que se active con un **marcador QR de diseño propio** y despliegue un **minijuego con tres modelos 3D de uso público** y controles táctiles. Mi respuesta fue *Bonk-a-Blox*: apuntas la cámara al marcador, aparece una isla flotante de bloques con tres hoyos y tienes 45 segundos para darle "bonk" a los personajes que se asoman… sin golpear la TNT.

**Herramientas.** Usé **MindAR** con **three.js** para que el juego corra en el navegador sin instalar nada. Modelé la isla, la TNT y el martillo en **Blender** con scripts de Python, así puedo regenerarlos cuando quiera. Los tres personajes son de **Blocky Characters de Kenney (licencia CC0)**, con animaciones de idle y caída. Los sonidos están sintetizados con la **Web Audio API** y la vibración usa la **Vibration API**.

**Proceso.** Empecé por el marcador. El QR lleva a la página del juego, así que escanearlo con la cámara normal abre la experiencia, y luego el juego usa esa misma imagen para rastrear. Después armé la isla en Blender, cuidando la escala (marcador = 1 unidad) y que cada modelo pese menos de 300 KB. Por último programé la lógica: aparición aleatoria, combos, corazones, dificultad que sube con el tiempo y pantalla final con precisión y récord.

**Retos.**
- *Un QR solo es mal marcador:* sus patrones repetitivos confunden al rastreador. Lo rodeé con un marco de bloques de colores distinto en cada lado y le agregué ilustraciones asimétricas. También usé corrección de errores nivel H para que el código siguiera leyéndose con el diseño encima.
- *Escalas:* MindAR trabaja en píxeles del marcador y los personajes de Kenney miden 2.7 unidades. Normalicé todo midiendo la caja de cada modelo.
- *Tocar algo pequeño en 3D:* agregué cajas invisibles más grandes sobre cada hoyo y botones 1-2-3 del mismo color que los hoyos.
- *Perder el marcador:* el juego se pausa solo y te pide volver a apuntar.

**Resultado.** Un juego corto y rápido con objetivo, reglas, puntaje y final claros. Cada toque responde con animación, partículas, sonido y vibración. Lo probé en *(teléfono 1)* y *(teléfono 2)* a varias distancias del marcador.

🎥 *(video o GIF aquí)*
🎮 Juega: https://rosaurarosauraaa.github.io/bonk-a-blox-qr/
💻 Código: https://github.com/Rosaurarosauraaa/bonk-a-blox-qr

#RealidadAumentada #WebAR #threejs #Blender #MindAR #GameDev
