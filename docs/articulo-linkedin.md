# Bonk-a-Blox: un minijuego de Realidad Aumentada que vive dentro de un código QR

**Objetivo:** 
En la asignatura de Realidad Virtual y Aumentada el reto consistió en diseñar una experiencia de RA para celular que se activara mediante un marcador QR diseñado por nosotros mismos y que desarrollara un minijuego con tres modelos 3D de dominio público y controles táctiles. Mi respuesta fue Bonk-a-Blox: apuntas la cámara al marcador, sale una isla flotante de bloques con tres hoyos y tienes 45 segundos para darle bonk a los personajes que aparecen… sin tocar la TNT.

**Herramientas:** 
Usé MindAR con three.js para que el juego se pueda jugar en el navegador sin instalar nada. Modelé la isla, la TNT y el martillo en Blender con scripts en Python, de esa forma puedo volver a generarlos cuando quiera. Los tres personajes son de Blocky Characters de Kenney (Licencia CC0), con animaciones de idle y caída. Los sonidos son sintetizados con la Web Audio API y la vibración usa la Vibration API.

**Proceso:** 
Comencé por el puntero. El QR apunta a la página del juego, de forma que si lo escaneas con la cámara normal se abre la experiencia y luego el juego utiliza esa misma imagen para hacer el seguimiento. Luego armé la isla en Blender, respetando la escala (marcador = 1 unidad) y que cada modelo pesase menos de 300 KB. Por último programé la lógica: aparición aleatoria, combos, corazones, dificultad que aumenta con el tiempo y pantalla final con precisión y récord.

**Retos:**
Un QR solo es mal marcador: sus patrones repetitivos confunden al rastreador. Lo rodeé con un marco de bloques de colores distinto en cada lado y le agregué ilustraciones asimétricas. También usé corrección de errores nivel H para que el código siguiera leyéndose con el diseño encima.
Escalas: MindAR trabaja en píxeles del marcador y los personajes de Kenney miden 2.7 unidades. Normalicé todo midiendo la caja de cada modelo.
Tocar algo pequeño en 3D: agregué cajas invisibles más grandes sobre cada hoyo y botones 1-2-3 del mismo color que los hoyos.
Perder el marcador: el juego se pausa solo y te pide volver a apuntar.

**Resultado:** 
Un juego corto y rápido con objetivo, reglas, puntaje y final claros. Cada toque responde con animación, partículas, sonido y vibración.

Juega: https://rosauraaa.github.io/blonk-a-roblox-qr/ 

Repositorio: https://github.com/rosauraaa/blonk-a-roblox-qr

#RealidadAumentada #WebAR #threejs #Blender #MindAR #GameDev
