# App de la paleta

App web que se conecta a la paleta por Bluetooth (Web Bluetooth) y muestra cada golpe con un consejo. Es un solo archivo, `index.html`; los modelos 3D son `paleta.glb` (8 KB, el de siempre) y `paleta2.glb` (156 KB, con animacion).

**Publicada en:** https://mateoherrera-dev.github.io/paleta-pingpong/app/ (GitHub Pages publica `main` sola, 1 o 2 minutos despues de cada merge).

## Como conectarla

1. **Navegador:** Chrome en Android o en la compu. En iPhone, Safari y Chrome no tienen Bluetooth web: usar la app **Bluefy**.
2. **En Android:** Bluetooth y ubicacion prendidos, y el permiso **"Dispositivos cercanos"** de Chrome (Ajustes → Aplicaciones → Chrome → Permisos). Sin ese permiso no aparece la lista de dispositivos.
3. **La paleta prendida** (por USB a la compu o al powerbank). Al prenderla tiene que quedar quieta 1 s para calibrar el giroscopio.
4. Abrir la app y **recargarla** para tener la ultima version. Con datos moviles el visor 3D puede no cargar (sus librerias vienen de cdnjs y jsdelivr): con wifi anda; sin el visor la app igual funciona y lo avisa.
5. Tocar **"Conectar paleta"** y elegir **"Paleta"**. Arriba tiene que decir "Conectada (20 B · Cuaternion 3D)" despues del primer golpe.

La placa acepta hasta 3 conexiones a la vez (por ejemplo, dos celulares y la compu). Si la placa se reinicia (desenchufarla, o cerrar y abrir `grabar.py`), se corta el Bluetooth: hay que volver a tocar "Conectar paleta".

**Sin la placa:** "Simulador" manda golpes inventados cada 2,5 s. En la compu se puede servir local con `python -m http.server 8000` desde la raiz del repo y abrir `http://localhost:8000/app/` (Web Bluetooth anda en `localhost` y en https, no en una IP de la red).

## Que muestra

En cada golpe llega por Bluetooth un mensaje de 20 bytes (`docs/CONTRATOS.md`, seccion 5): tipo de golpe, confianza del modelo, velocidad, angulo de la cara, pico de giro y la orientacion de la paleta.

| Parte | Que es |
| --- | --- |
| **Golpe** | Lo que dijo el modelo: topspin o empuje, de derecha o de reves. El firmware no manda lo que el modelo llama ruido ni los swings de menos de 300 °/s, asi que esos golpes no aparecen. |
| **Visor 3D** | La paleta en el instante del impacto, con la cara que golpeo mirando a la camara. El rumbo (para donde apuntaba en el plano) se descarta porque sin magnetometro se corre con el tiempo. Se puede girar arrastrando; el boton de la goma la da vuelta. |
| **Angulo** | Inclinacion de la cara que golpeo: 0° = vertical, **negativo = cerrada** (mira a la mesa), **positivo = abierta** (mira al techo). La goma es la del agarre fijo: derecha con la negra, reves con la roja. |
| **Velocidad** | Velocidad de la paleta estimada con el giro (v = ω · r), en km/h. |
| **Timing (pico)** | Cuantos ms antes (−) o despues (+) del impacto giro mas rapido la paleta. |
| **Consejo** | Sale de comparar el angulo con el rango de cada golpe y el pico con los limites (abajo). Con la casilla, lo lee en voz alta. |
| **Esta sesion / Ultimos golpes** | Cuantos de cada tipo y los ultimos 15. |
| **Diagnostico** (desplegable) | Todos los campos crudos del mensaje y los ultimos 10 golpes. Sirve para comparar con lo que imprime la placa por serie. |

## Criterios de los consejos

Estan en `CRITERIOS` y `PICO_*` al principio del `<script>` de `index.html`, y tienen que coincidir con `docs/GOLPES.md`.

| Golpe | Angulo ideal | Pico |
| --- | --- | --- |
| Topspin de derecha (TD) | −25° a +5° | entre −25 y +30 ms |
| Topspin de reves (TR) | −30° a 0° | entre −25 y +30 ms |
| Empuje de derecha (ED) | +30° a +50° | no se mira |
| Empuje de reves (ER) | +25° a +45° | no se mira |

Si la confianza del modelo es menor a 55 %, dice "Gesto poco claro" en vez de dar un consejo. Los rangos de topspin se ajustaron el 6/11 con lo medido en la mesa (ver la nota en `docs/GOLPES.md`).

## Correcciones que hace la app

- **Cara en los empujes:** el firmware elige la cara por el sentido del giro antes del impacto y en los empujes a veces elige la otra (el angulo sale con el signo cambiado). Si el modelo reconocio el golpe, la app recalcula el angulo desde el cuaternion con la goma del agarre fijo.
- **Mensajes de 14 bytes:** el firmware viejo no manda la orientacion. La app los acepta igual; el visor muestra solo la inclinacion.
