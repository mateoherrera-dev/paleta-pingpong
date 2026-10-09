# Criterios Biomecanicos y Reglas de Retroalimentacion

Este documento compila los fundamentos tecnicos de los cuatro golpes base analizados en las lecciones de *PingSkills*, su traduccion a signaturas inerciales (IMU MPU-6500) y las reglas deterministicas para la generacion automatica de feedback en la aplicacion.

---

## 1. Arquitectura del Sistema de Retroalimentacion

El sistema opera mediante una separacion estricta entre la **clasificacion de intencion motora** y la **evaluacion de calidad tecnica**:

1. **Clasificacion (Edge Impulse / TinyML):** Identifica el gesto ejecutado (`TD`, `TR`, `ED` o `ER`).
2. **Extraccion Cinematica:** Calcula de forma deterministica:
   * $\theta_{\text{impacto}}$: Inclinacion angular de la cara de la paleta en el choque (grados respecto a la vertical, donde $0^\circ$ es perpendicular a la mesa, valores negativos miran hacia abajo y positivos hacia el techo).
   * $\omega_{\max}$: Velocidad angular pico del swing.
   * $\Delta t_{\text{pico}} = t_{\omega_{\max}} - t_{\text{impacto}}$: Desfasaje temporal entre el punto de maxima aceleracion angular y el contacto con la pelota.
   * $\text{Giro}_{\text{lateral}}$: Componente de rotacion fuera del plano principal de avance.
3. **Motor de Reglas Condicional:** Aplica umbrales heuristicos especificos para la clase detectada y selecciona una unica recomendacion prioritaria.

---

## 2. Analisis por Golpe

### A. Topspin de Derecha contra Corte (Forehand Topspin Against Backspin — TD)
https://www.youtube.com/watch?v=_Bi3vOTH_do

#### Tecnica segun PingSkills
* **Posicion inicial y trayectoria:** La paleta arranca baja, a la altura de la rodilla (*knee high*), con la cara levemente abierta para poder entrar bajo el efecto cortado rival.
* **Contacto y terminacion:** El contacto exige un raspado ascendente (*brushing action*). La trayectoria debe ser marcadamente vertical, finalizando por encima del nivel de los ojos (*above eye level*) con una flexion angular aproximada de 90° en el codo.
* **Errores frecuentes:** Iniciar el swing a la altura de la mesa (demasiado alto), avanzar con trayectoria puramente horizontal o entrar con la cara excesivamente cerrada, lo que impide contrarrestar el backspin entrante y envia la bola a la red.

#### Signatura Inercial (IMU)
* Vector de aceleracion vertical marcadamente positivo en la ventana previa al impacto (transicion desde altura de rodilla hacia arriba).
* Rotacion horaria de antebrazo/muñeca en el eje longitudinal/transversal.
* Pico de velocidad angular $\omega_{\max}$ alineado con el instante del choque.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[-30^\circ, -10^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Aceleracion vertical minima previa:** $a_{\text{vertical}} \ge a_{\text{min\_lift}}$

```text
SI a_vertical < a_min_lift:
    RETORNAR "Inicia el swing mas abajo (altura de rodilla) y termina sobre los ojos para levantar la bola."
SINO SI θ_impacto > +5°:
    RETORNAR "Cara excesivamente abierta; cerra levemente la paleta para que no flote al fondo."
SINO SI θ_impacto < -35°:
    RETORNAR "Cara muy cerrada; estas tapando la pelota y el corte rival la tirara a la red."
SINO SI Δt_pico < -35 ms:
    RETORNAR "Estas frenando la mano antes del contacto; acelera a traves de la pelota."
SINO:
    RETORNAR "Topspin de derecha optimo: trayectoria ascendente y aceleracion fluida."
```

---

### B. Topspin de Reves contra Corte (Backhand Topspin — TR)
https://www.youtube.com/watch?v=LmQNDC-1Ew0

#### Tecnica segun PingSkills
* **Posicion inicial:** La paleta debe descender al menos hasta la altura de las rodillas para situarse por debajo de la trayectoria de la bola y permitir una trayectoria de elevacion neta.
* **Extension y aceleracion:** El contacto exige un raspado fino. El swing no debe interrumpirse al momento del choque: el brazo y la muñeca deben proyectarse hacia arriba hasta superar la altura de la cabeza, permitiendo que la paleta sobrepase la linea del codo (*swing past your elbow*).
* **Errores frecuentes:** Desacelerar la mano por miedo a fallar, o no descender lo suficiente en la preparacion, provocando que la rotacion contraria de la pelota entrante (backspin) la arrastre directo a la red.

#### Signatura Inercial (IMU)
* Inversion de polaridad en el giroscopio respecto al topspin de derecha (movimiento de supinacion y extension de reves).
* Elevacion marcada del vector de aceleracion lineal previo al choque.
* Curva de velocidad angular pronunciada con pico sostenido durante el *follow-through*.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[-35^\circ, -15^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Intensidad angular ($\omega_{\max}$):** Debe superar el umbral minimo de aceleracion del swing ($\omega_{\text{min\_tr}}$).

```{text}
SI θ_impacto > 0°:
RETORNAR "Entraste con la cara abierta; inclina la paleta hacia la mesa para superar la red."
SINO SI Δt_pico < -35 ms O ω_max < ω_min_tr:
RETORNAR "No cortes el golpe; deja que la paleta pase la linea del codo con aceleracion continua."
SINO SI θ_impacto < -45°:
RETORNAR "Angulo excesivamente cerrado; abri ligeramente la cara para dar altura al tiro."
SINO:
RETORNAR "Topspin de reves consistente: buena extension y raspado."
```

---

### C. Empuje de Derecha (Forehand Push — ED)
https://www.youtube.com/watch?v=x6wQmAoTA_o&t=1s 

#### Tecnica segun PingSkills
* **Posicion y angulo de la cara:** La paleta se situa lateralmente con la cara inclinada hacia atras (*tilted back*, orientada hacia el techo) para entrar por debajo de la pelota y generar backspin defensivo.
* **Mecanica del brazo:** El agarre y los dedos deben mantenerse relajados. La paleta avanza hacia la mesa y hacia la red en linea recta. Si el jugador aprieta la empuñadura en exceso, la muñeca se bloquea y el brazo cruza el cuerpo en diagonal, perdiendo precision direccional.
* **Errores frecuentes:** Entrar con la cara vertical o cerrar el golpe antes de tiempo, impidiendo contrarrestar el efecto de la pelota entrante.

#### Signatura Inercial (IMU)
* Componente estatico de aceleracion previa con la normal de la pala orientada hacia arriba ($+a_z$).
* Aceleracion traslacional suave hacia el frente; valores moderados en giroscopios (golpe de control, no de potencia).
* Valores reducidos de rotacion en el eje lateral de la pala.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[+30^\circ, +50^\circ]$
* **Desviacion angular transversal ($\text{Giro}_{\text{lateral}}$):** $\le \text{Umbral}_{\text{cruzado}}$

```{text}
SI θ_impacto < +20°:
RETORNAR "Abri la cara de la paleta hacia arriba para entrar bien por debajo de la pelota."
SINO SI Giro_lateral > Umbral_cruzado:
RETORNAR "Relaja la muñeca: empuja recto hacia la red sin cruzar el brazo delante del pecho."
SINO SI θ_impacto > +60°:
RETORNAR "Paleta demasiado abierta; la pelota se elevara demasiado facilitando el remate rival."
SINO:
RETORNAR "Empuje de derecha correcto: angulo de corte limpio y trayectoria controlada."
```

---

### D. Empuje de Reves (Backhand Push — ER)
https://www.youtube.com/watch?v=hqiiVW7BG1A 

#### Tecnica segun PingSkills
* **Inicio y terminacion:** El movimiento se origina frente al cuerpo con la cara de la paleta abierta hacia atras. El contacto raspa la base inferior de la pelota y la terminacion avanza hacia adelante en direccion a la red.
* **Adaptacion al spin:** Ante pelotas rivales con fuerte corte, se requiere inclinar la cara mas hacia atras para neutralizar el backspin entrante y evitar que la pelota caiga en la red.
* **Errores frecuentes:** Golpear plano o con angulo neutro ($0^\circ$), provocando que el efecto descendente de la bola contraria la haga morir en la red de inmediato.

#### Signatura Inercial (IMU)
* Vector de aceleracion previo reflejando cara abierta al techo.
* Movimiento lineal corto y uniforme hacia la red.
* Choque elastico limpio con baja dispersion en aceleracion angular post-impacto.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[+25^\circ, +45^\circ]$

```{text}
SI θ_impacto < +15°:
RETORNAR "Inclina la paleta hacia atras; si entras plano el backspin rival mandara la bola a la red."
SINO SI θ_impacto > +55°:
RETORNAR "Cara excesivamente abierta; la pelota flotara alta sobre la mesa."
SINO SI Δt_pico < -40 ms:
RETORNAR "Empuja de forma fluida hacia la red; el movimiento se detuvo antes del contacto."
SINO:
RETORNAR "Empuje de reves solido: buena contencion y angulo adecuado."
```

---

## 3. Matriz Resumen de Parametros

| Golpe | Codigo ML | Angulo Optimo ($\theta$) | Condicion Critica de Falla | Consejo Prioritario |
| :--- | :---: | :---: | :--- | :--- |
| **Topspin Derecha** | `TD` | $-40^\circ \text{ a } -20^\circ$ | $\theta > -10^\circ$ (Impacto plano) | *"Cerra la cara de la paleta; el golpe fue muy plano."* |
| **Topspin Reves** | `TR` | $-35^\circ \text{ a } -15^\circ$ | $\Delta t_{\text{pico}} < -35\text{ ms}$ (Freno previo) | *"No cortes el movimiento; pasa la linea del codo."* |
| **Empuje Derecha** | `ED` | $+30^\circ \text{ a } +50^\circ$ | $\theta < +20^\circ$ o desvio lateral | *"Abri la cara y empuja recto hacia la red."* |
| **Empuje Reves** | `ER` | $+25^\circ \text{ a } +45^\circ$ | $\theta < +15^\circ$ (Entrada recta) | *"Inclina la paleta hacia atras para raspar por abajo."* |