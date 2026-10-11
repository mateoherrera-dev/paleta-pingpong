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

### A. Topspin de Derecha (Forehand Topspin — TD)
https://www.youtube.com/watch?v=_Bi3vOTH_do

*Condicion de captura:* Ejecucion sobre bola viva neutra mediante autopique (self-feed con la mano libre). Foco en arco ascendente y aceleracion fluida.

#### Tecnica segun PingSkills
* **Posicion inicial y trayectoria:** Al picar la bola uno mismo sobre la mesa, no existe backspin rival entrante. La paleta arranca a la altura de la cadera o mesa (no hace falta bajar hasta la rodilla), con la cara cerrada hacia la mesa para imprimir topspin y no tirar la bola larga fuera de la mesa.
* **Contacto y terminacion:** El contacto exige un raspado ascendente hacia adelante (*brushing action*). La trayectoria sube y avanza, terminando a la altura de la frente o los ojos con flexion de codo.
* **Errores frecuentes:** Entrar con la cara demasiado vertical o abierta ($\theta > -20^\circ$), lo que hace que la bola neutra vuele larga fuera de la mesa; o tapar excesivamente la pelota ($\theta < -60^\circ$) enviandola directo a la red.

#### Signatura Inercial (IMU)
* Vector de aceleracion vertical positivo en la ventana previa al impacto.
* Rotacion horaria de antebrazo/muñeca en el eje longitudinal/transversal.
* Pico de velocidad angular $\omega_{\max}$ alineado con el instante del choque.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[-50^\circ, -30^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Aceleracion vertical minima previa:** $a_{\text{vertical}} \ge a_{\text{min\_lift}}$

```text
SI a_vertical < a_min_lift:
    RETORNAR "Acompaña la trayectoria de abajo hacia arriba para imprimir efecto topspin."
SINO SI θ_impacto > -20°:
    RETORNAR "Cara excesivamente abierta para bola neutra; cerra la paleta hacia la mesa para no tirarla larga."
SINO SI θ_impacto < -60°:
    RETORNAR "Cara excesivamente cerrada; estas tapando la pelota y chocara contra la red."
SINO SI Δt_pico < -35 ms:
    RETORNAR "Estas frenando la mano antes del contacto; acelera a traves de la pelota."
SINO:
    RETORNAR "Topspin de derecha optimo: arco ascendente fluido y buen raspado."
```

---

### B. Topspin de Reves (Backhand Topspin — TR)
https://www.youtube.com/watch?v=LmQNDC-1Ew0

*Condicion de captura:* Ejecucion sobre bola viva neutra mediante autopique (self-feed con la mano libre).

#### Tecnica segun PingSkills
* **El codo como bisagra (pivote adelantado):** El codo se coloca adelantado respecto al torso, flexionado a unos 90° y apuntando hacia la red. Actua como un punto de pivote fijo y estable: el antebrazo y la muñeca se pliegan hacia el estomago y luego se extienden y rotan hacia arriba y adelante alrededor de ese eje en un movimiento de latigo.
* **Extension y terminacion:** Raspado fino ascendente y hacia adelante. El antebrazo se proyecta hacia la red superando la linea del codo (*swing past your elbow*).
* **Errores frecuentes:**
  - *Codo abierto al costado:* Si el codo se va hacia el lateral del cuerpo, se bloquea la articulacion, se pierde el recorrido del antebrazo y se fuerza un empuje rigido con todo el hombro ("movimiento tipo puerta"), desplomando la velocidad angular.
  - *Cara abierta:* Entrar con $\theta > -15^\circ$ hace que la bola neutra vuele larga fuera de la mesa.

#### Signatura Inercial (IMU)
* **Latigo vs. puerta:** Si el codo actua como pivote, el sensor en el pomo registra un pico pronunciado y concentrado de velocidad angular ($\omega_{\max}$) gracias al radio de giro del antebrazo. Si se empuja con el hombro rigido, $\omega$ queda bajo y disperso en el tiempo.
* Inversion de polaridad en el giroscopio respecto al topspin de derecha (movimiento de supinacion y extension de reves).
* Curva de aceleracion angular pronunciada con pico sostenido durante el *follow-through*.

#### Reglas Deterministicas de Evaluacion
* **Rango ideal de angulo ($\theta_{\text{impacto}}$):** $[-45^\circ, -25^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Intensidad angular ($\omega_{\max}$):** Debe superar el umbral minimo de aceleracion del swing ($\omega_{\text{min\_tr}}$).

```text
SI θ_impacto > -15°:
    RETORNAR "Cara demasiado abierta; cerra la paleta hacia la mesa para que el topspin baje a tiempo."
SINO SI ω_max < ω_min_tr:
    RETORNAR "Usa el codo adelantado como bisagra y acelera el antebrazo; no empujes rigido con el hombro."
SINO SI Δt_pico < -35 ms:
    RETORNAR "No cortes el golpe; deja que la paleta pase la linea del codo con aceleracion continua."
SINO SI θ_impacto < -55°:
    RETORNAR "Angulo excesivamente cerrado; abri ligeramente la cara para superar la red."
SINO:
    RETORNAR "Topspin de reves consistente: buen pivote de codo y raspado fluido."
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
| **Topspin Derecha** | `TD` | $-50^\circ \text{ a } -30^\circ$ | $\theta > -20^\circ$ (Cara muy abierta) | *"Cerra la cara de la paleta; el golpe fue muy plano/abierto."* |
| **Topspin Reves** | `TR` | $-45^\circ \text{ a } -25^\circ$ | $\theta > -15^\circ$ (Cara muy abierta) | *"Cerra la paleta hacia la mesa para que el topspin baje."* |
| **Empuje Derecha** | `ED` | $+30^\circ \text{ a } +50^\circ$ | $\theta < +20^\circ$ o desvio lateral | *"Abri la cara y empuja recto hacia la red."* |
| **Empuje Reves** | `ER` | $+25^\circ \text{ a } +45^\circ$ | $\theta < +15^\circ$ (Entrada recta) | *"Inclina la paleta hacia atras para raspar por abajo."* |