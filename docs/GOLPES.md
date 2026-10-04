# Criterios Biomecánicos y Reglas de Retroalimentación

Este documento compila los fundamentos técnicos de los cuatro golpes base analizados en las lecciones de *PingSkills*, su traducción a signaturas inerciales (IMU MPU-6500) y las reglas determinísticas para la generación automática de feedback en la aplicación.

---

## 1. Arquitectura del Sistema de Retroalimentación

El sistema opera mediante una separación estricta entre la **clasificación de intención motora** y la **evaluación de calidad técnica**:

1. **Clasificación (Edge Impulse / TinyML):** Identifica el gesto ejecutado (`TD`, `TR`, `ED` o `ER`).
2. **Extracción Cinemática:** Calcula de forma determinística:
   * $\theta_{\text{impacto}}$: Inclinación angular de la cara de la paleta en el choque (grados respecto a la vertical, donde $0^\circ$ es perpendicular a la mesa, valores negativos miran hacia abajo y positivos hacia el techo).
   * $\omega_{\max}$: Velocidad angular pico del swing.
   * $\Delta t_{\text{pico}} = t_{\omega_{\max}} - t_{\text{impacto}}$: Desfasaje temporal entre el punto de máxima aceleración angular y el contacto con la pelota.
   * $\text{Giro}_{\text{lateral}}$: Componente de rotación fuera del plano principal de avance.
3. **Motor de Reglas Condicional:** Aplica umbrales heurísticos específicos para la clase detectada y selecciona una única recomendación prioritaria.

---

## 2. Análisis por Golpe

### A. Topspin de Derecha contra Corte (Forehand Topspin Against Backspin — TD)
https://www.youtube.com/watch?v=_Bi3vOTH_do

#### Técnica según PingSkills
* **Posición inicial y trayectoria:** La paleta arranca baja, a la altura de la rodilla (*knee high*), con la cara levemente abierta para poder entrar bajo el efecto cortado rival.
* **Contacto y terminación:** El contacto exige un raspado ascendente (*brushing action*). La trayectoria debe ser marcadamente vertical, finalizando por encima del nivel de los ojos (*above eye level*) con una flexión angular aproximada de 90° en el codo.
* **Errores frecuentes:** Iniciar el swing a la altura de la mesa (demasiado alto), avanzar con trayectoria puramente horizontal o entrar con la cara excesivamente cerrada, lo que impide contrarrestar el backspin entrante y envía la bola a la red.

#### Signatura Inercial (IMU)
* Vector de aceleración vertical marcadamente positivo en la ventana previa al impacto (transición desde altura de rodilla hacia arriba).
* Rotación horaria de antebrazo/muñeca en el eje longitudinal/transversal.
* Pico de velocidad angular $\omega_{\max}$ alineado con el instante del choque.

#### Reglas Determinísticas de Evaluación
* **Rango ideal de ángulo ($\theta_{\text{impacto}}$):** $[-30^\circ, -10^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Aceleración vertical mínima previa:** $a_{\text{vertical}} \ge a_{\text{min\_lift}}$

```text
SI a_vertical < a_min_lift:
    RETORNAR "Iniciá el swing más abajo (altura de rodilla) y terminá sobre los ojos para levantar la bola."
SINO SI θ_impacto > +5°:
    RETORNAR "Cara excesivamente abierta; cerrá levemente la paleta para que no flote al fondo."
SINO SI θ_impacto < -35°:
    RETORNAR "Cara muy cerrada; estás tapando la pelota y el corte rival la tirará a la red."
SINO SI Δt_pico < -35 ms:
    RETORNAR "Estás frenando la mano antes del contacto; acelerá a través de la pelota."
SINO:
    RETORNAR "Topspin de derecha óptimo: trayectoria ascendente y aceleración fluida."
```

---

### B. Topspin de Revés contra Corte (Backhand Topspin — TR)
https://www.youtube.com/watch?v=LmQNDC-1Ew0

#### Técnica según PingSkills
* **Posición inicial:** La paleta debe descender al menos hasta la altura de las rodillas para situarse por debajo de la trayectoria de la bola y permitir una trayectoria de elevación neta.
* **Extensión y aceleración:** El contacto exige un raspado fino. El swing no debe interrumpirse al momento del choque: el brazo y la muñeca deben proyectarse hacia arriba hasta superar la altura de la cabeza, permitiendo que la paleta sobrepase la línea del codo (*swing past your elbow*).
* **Errores frecuentes:** Desacelerar la mano por miedo a fallar, o no descender lo suficiente en la preparación, provocando que la rotación contraria de la pelota entrante (backspin) la arrastre directo a la red.

#### Signatura Inercial (IMU)
* Inversión de polaridad en el giroscopio respecto al topspin de derecha (movimiento de supinación y extensión de revés).
* Elevación marcada del vector de aceleración lineal previo al choque.
* Curva de velocidad angular pronunciada con pico sostenido durante el *follow-through*.

#### Reglas Determinísticas de Evaluación
* **Rango ideal de ángulo ($\theta_{\text{impacto}}$):** $[-35^\circ, -15^\circ]$
* **Tolerancia de timing ($\Delta t_{\text{pico}}$):** $\ge -25\text{ ms}$
* **Intensidad angular ($\omega_{\max}$):** Debe superar el umbral mínimo de aceleración del swing ($\omega_{\text{min\_tr}}$).

```{text}
SI θ_impacto > 0°:
RETORNAR "Entraste con la cara abierta; incliná la paleta hacia la mesa para superar la red."
SINO SI Δt_pico < -35 ms O ω_max < ω_min_tr:
RETORNAR "No cortes el golpe; dejá que la paleta pase la línea del codo con aceleración continua."
SINO SI θ_impacto < -45°:
RETORNAR "Ángulo excesivamente cerrado; abrí ligeramente la cara para dar altura al tiro."
SINO:
RETORNAR "Topspin de revés consistente: buena extensión y raspado."
```

---

### C. Empuje de Derecha (Forehand Push — ED)
https://www.youtube.com/watch?v=x6wQmAoTA_o&t=1s 

#### Técnica según PingSkills
* **Posición y ángulo de la cara:** La paleta se sitúa lateralmente con la cara inclinada hacia atrás (*tilted back*, orientada hacia el techo) para entrar por debajo de la pelota y generar backspin defensivo.
* **Mecánica del brazo:** El agarre y los dedos deben mantenerse relajados. La paleta avanza hacia la mesa y hacia la red en línea recta. Si el jugador aprieta la empuñadura en exceso, la muñeca se bloquea y el brazo cruza el cuerpo en diagonal, perdiendo precisión direccional.
* **Errores frecuentes:** Entrar con la cara vertical o cerrar el golpe antes de tiempo, impidiendo contrarrestar el efecto de la pelota entrante.

#### Signatura Inercial (IMU)
* Componente estático de aceleración previa con la normal de la pala orientada hacia arriba ($+a_z$).
* Aceleración traslacional suave hacia el frente; valores moderados en giroscopios (golpe de control, no de potencia).
* Valores reducidos de rotación en el eje lateral de la pala.

#### Reglas Determinísticas de Evaluación
* **Rango ideal de ángulo ($\theta_{\text{impacto}}$):** $[+30^\circ, +50^\circ]$
* **Desviación angular transversal ($\text{Giro}_{\text{lateral}}$):** $\le \text{Umbral}_{\text{cruzado}}$

```{text}
SI θ_impacto < +20°:
RETORNAR "Abrí la cara de la paleta hacia arriba para entrar bien por debajo de la pelota."
SINO SI Giro_lateral > Umbral_cruzado:
RETORNAR "Relajá la muñeca: empujá recto hacia la red sin cruzar el brazo delante del pecho."
SINO SI θ_impacto > +60°:
RETORNAR "Paleta demasiado abierta; la pelota se elevará demasiado facilitando el remate rival."
SINO:
RETORNAR "Empuje de derecha correcto: ángulo de corte limpio y trayectoria controlada."
```

---

### D. Empuje de Revés (Backhand Push — ER)
https://www.youtube.com/watch?v=hqiiVW7BG1A 

#### Técnica según PingSkills
* **Inicio y terminación:** El movimiento se origina frente al cuerpo con la cara de la paleta abierta hacia atrás. El contacto raspa la base inferior de la pelota y la terminación avanza hacia adelante en dirección a la red.
* **Adaptación al spin:** Ante pelotas rivales con fuerte corte, se requiere inclinar la cara más hacia atrás para neutralizar el backspin entrante y evitar que la pelota caiga en la red.
* **Errores frecuentes:** Golpear plano o con ángulo neutro ($0^\circ$), provocando que el efecto descendente de la bola contraria la haga morir en la red de inmediato.

#### Signatura Inercial (IMU)
* Vector de aceleración previo reflejando cara abierta al techo.
* Movimiento lineal corto y uniforme hacia la red.
* Choque elástico limpio con baja dispersión en aceleración angular post-impacto.

#### Reglas Determinísticas de Evaluación
* **Rango ideal de ángulo ($\theta_{\text{impacto}}$):** $[+25^\circ, +45^\circ]$

```{text}
SI θ_impacto < +15°:
RETORNAR "Incliná la paleta hacia atrás; si entrás plano el backspin rival mandará la bola a la red."
SINO SI θ_impacto > +55°:
RETORNAR "Cara excesivamente abierta; la pelota flotará alta sobre la mesa."
SINO SI Δt_pico < -40 ms:
RETORNAR "Empujá de forma fluida hacia la red; el movimiento se detuvo antes del contacto."
SINO:
RETORNAR "Empuje de revés sólido: buena contención y ángulo adecuado."
```

---

## 3. Matriz Resumen de Parámetros

| Golpe | Código ML | Ángulo Óptimo ($\theta$) | Condición Crítica de Falla | Consejo Prioritario |
| :--- | :---: | :---: | :--- | :--- |
| **Topspin Derecha** | `TD` | $-40^\circ \text{ a } -20^\circ$ | $\theta > -10^\circ$ (Impacto plano) | *"Cerrá la cara de la paleta; el golpe fue muy plano."* |
| **Topspin Revés** | `TR` | $-35^\circ \text{ a } -15^\circ$ | $\Delta t_{\text{pico}} < -35\text{ ms}$ (Freno previo) | *"No cortes el movimiento; pasá la línea del codo."* |
| **Empuje Derecha** | `ED` | $+30^\circ \text{ a } +50^\circ$ | $\theta < +20^\circ$ o desvío lateral | *"Abrí la cara y empujá recto hacia la red."* |
| **Empuje Revés** | `ER` | $+25^\circ \text{ a } +45^\circ$ | $\theta < +15^\circ$ (Entrada recta) | *"Incliná la paleta hacia atrás para raspar por abajo."* |