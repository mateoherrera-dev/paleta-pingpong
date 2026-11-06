# Manual de Identidad y Sistema de Marca: DOC

Este documento define la personalidad, narrativa, tono de voz y sistema visual de **DOC**, sirviendo como guia rectora para el diseño de la aplicacion web, la presentacion publica y la coherencia del proyecto.

---

## 1. El Concepto y el Nombre: DOC

### El Arquetipo
DOC no es un sistema de laboratorio ni una tesis de fisica teorica. DOC es el **entrenador de rincon** (*corner coach*):
* El tipo con experiencia que te mira desde el banco, te canta la justa sin vueltas y te acomoda la toalla.
* No te abruma con formulas abstractas de cinemática; te da la correccion milimetrica que necesitas antes del siguiente punto: *"Cerra la cara 10 grados, le estas pegando muy abierta"* o *"Acelera la muñeca antes del impacto"*.
* Combina autoridad, cercania y rigor tecnico.

### La Sigla Institucional
Para ambitos academicos, jurados o la documentacion de ingenieria, el nombre se desglosa naturalmente en:
> **DOC: Datos y Orientacion en Cancha**

Habla el idioma del deporte y del tenis de mesa real, manteniendo un respaldo tecnico creible.

---

## 2. El Manifiesto de Marca: FIND YOUR EDGE

El lema central que sintetiza el producto es:

> # FIND YOUR EDGE

El termino **"Edge"** condensa una triple dimension deliberada:

1. **El canto de la mesa (The Edge of the table):**
   La pelota que roza la linea blanca o el canto de la mesa es el tiro definitivo, inalcanzable, el punto que nadie puede levantar.
2. **Tu ventaja competitiva (Having an edge):**
   El plus tactico y tecnico milimetrico sobre el rival en cada intercambio.
3. **Tu propio limite (Pushing your edge):**
   Descubrir hasta donde podes acelerar el brazo y cerrar la cara sin perder el control de la pelota.
4. *(Guiño de ingenieria):* Vincula sutilmente con **Edge Impulse** y el procesamiento de **TinyML en el edge** (en el microcontrolador ESP32-S3), sin necesidad de saturar al usuario con tecnicismos.

---

## 3. Tono de Voz y Comunicacion

* **Directo y accionable:** Mensajes concisos orientados a la correccion del golpe en mesa.
* **Cercano pero exigente:** Festeja los tiros optimos (score $> 80$), pero avisa de inmediato las fallas criticas (cara abierta en topspin, aceleracion tardia).
* **Sin jerga innecesaria:** Evitar terminos frios como "algoritmo clasificador", "red neuronal densa", o "cuaternion de rotacion" en la cara del usuario. Usar "clasificacion del golpe", "angulo de cara", "velocidad" y "timing".

---

## 4. Paleta Cromatica y Materiales

| Token | Hex | Nombre | Rol en el producto |
| :--- | :--- | :--- | :--- |
| `--color-ball-orange` | `#ff7700` | Naranja Celuloide Torneo | Color identitario primario. Fondo de la landing e intro de la pelota de 40 mm. |
| `--color-ink-navy` | `#0f172a` | Azul Marino Grafito Mate | Tinta industrial estampada en la pelota, tipografia principal y botones primarios. |
| `--color-table-dark` | `#0c1322` | Grafito Mesa de Torneo | Fondo del dashboard de telemetria y modo oscuro de entrenamiento. |
| `--color-table-card` | `#162035` | Azul Tablero HUD | Fondo de las tarjetas y paneles de datos del golpe. |
| `--color-rubber-red` | `#dc2626` | Rojo Goma de Reves | Identificador de goma de reves ($+Z$), fallas criticas y alertas. |
| `--color-rubber-black`| `#111827` | Negro Goma de Derecha | Identificador de goma de derecha ($-Z$). |
| `--color-optimal-green`| `#10b981`| Verde Acierto ITTF | Rango de angulo optimo, score alto ($\ge 80\text{ pts}$) e indicador de conexion. |
| `--color-warn-amber` | `#f59e0b` | Amarillo de Ajuste | Zona aceptable pero mejorable ($40-74\text{ pts}$). |

---

## 5. El Sello Industrial (Ball Stamp)

Inspirado en los sellos oficiales de torneos de la ITTF (Nittaku, DHS, Butterfly):

```text
       DOC
     ★ ★ ★
      40+
```

* **`DOC`:** Tipografia sans-serif pesada (`font-weight: 900`), mayuscula, con espaciado amplio (`letter-spacing: 0.14em`).
* **`★ ★ ★`:** Tres estrellas que representan precision, calidad de torneo y validacion de impacto.
* **`40+`:** La especificacion oficial de diametro en milimetros de las pelotas reglamentarias de poliplastico/celuloide.

---

## 6. Principios de Diseño para la App Web

1. **La pantalla de inicio es pura y nítida:**
   La landing arranca en un plano 2D vectorial con el cuño `DOC ★★★ 40+` y el lema `FIND YOUR EDGE`. Nada de deformaciones extrañas ni ojos de pez.
2. **Hand-off instantaneo de capas:**
   Al tocar `COMENZAR`, la capa 2D se intercambia de inmediato por el lienzo WebGL en el mismo fotograma. La pelota fisica toma el protagonismo, cae, pica en la mesa con el sonido del celuloide y da paso al dashboard.
3. **Telemetria HUD deportiva:**
   El dashboard presenta los tres datos clave del swing de un vistazo:
   * **Angulo de cara ($\theta$):** Con indicador visual de cara cerrada/abierta.
   * **Velocidad ($v$ en km/h):** Estimada a partir del giro angular.
   * **Score Tecnico (1 a 100):** Evaluacion continua con penalizacion gaussiana.
4. **Claridad en los tres modos:**
   * **🎯 Modo Libre:** Practica cotidiana con visor 3D interactivo y consejo de audio instantaneo.
   * **🎓 Modo Tutorial:** Progresion de 3 pasos basada en *PingSkills* (Angulo $\rightarrow$ Brushing $\rightarrow$ Latigo).
   * **📊 Modo Test:** Validacion de precision del modelo TinyML con contador de aciertos frente al umbral del MVP ($80\,\%$).
