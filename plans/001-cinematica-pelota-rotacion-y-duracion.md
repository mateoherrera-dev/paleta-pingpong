# 001 — Calibrar rotación, duración y resolución de la cinemática 3D

- **Status**: DONE
- **Commit**: 6f5b634
- **Severity**: HIGH
- **Category**: Easing & duration / Physicality
- **Estimated scope**: 1 file (`app/index.html`), ~40 lines

## Problem

En `app/index.html:2205-2240`, la cinemática de la pelota dura 1550 ms y gira a una velocidad angular extrema (`spinT * Math.PI * 6.5`, más de 3 vueltas completas en un segundo y medio). Esto produce un efecto estroboscópico vertiginoso donde el texto `DOC` se emparenta con un borrón ilegible, la animación se siente interminable ("no tiene fin") y no comunica un aterrizaje claro hacia el dashboard.

```javascript
/* app/index.html:2205-2230 — current */
const dur = 1550;
const spinT = Math.pow(t, 1.25);
introBall.rotation.x = spinT * Math.PI * 6.5; 
introBall.rotation.y = 0.35 * Math.sin(t * Math.PI);
introBall.rotation.z = -0.12 * Math.sin(t * Math.PI);
```

## Target

Reducir la duración total a 950 ms (decisiva, ágil). Limitar la rotación en X a un arco natural de topspin controlado ($\approx 1.2\pi$, poco más de media vuelta) para que el cuño `DOC` y las estrellas sean legibles mientras la luz especular barre la superficie sin estroboscopía. La caída hacia el borde inferior debe ser limpia, lineal-acelerada y permitir desestimación inmediata al segundo toque:

```javascript
/* target */
const dur = 950;
const ease = 1 - Math.pow(1 - t, 3.5);
introCamera.position.z = zStart + (zEnd - zStart) * ease;

// Rotación suave y legible: 1 vuelta parcial de topspin
introBall.rotation.x = ease * Math.PI * 1.35;
introBall.rotation.y = 0.22 * Math.sin(ease * Math.PI);
introBall.rotation.z = -0.06 * Math.sin(ease * Math.PI);

// Descenso y salida limpia por el borde inferior a partir de t=0.35
if (t <= 0.30) {
  introBall.position.y = 0.012 * Math.sin((t / 0.30) * Math.PI * 0.5);
} else {
  const tau = (t - 0.30) / 0.70;
  introBall.position.y = 0.012 - 0.24 * (tau * tau);
}
```

## Repo conventions to follow

- Las funciones de cinemática viven en el script de `app/index.html` bajo la cabecera `// CINEMÁTICA DIRECTA DE LA PELOTA (OPCIÓN A)`.
- La función `cerrarIntro()` oculta `#intro-stage` y apaga el render loop.

## Steps

1. En `app/index.html`, ubicar la función `dispararIntroCinematica()`.
2. Modificar la constante `dur` de `1550` a `950`.
3. Reemplazar la fórmula de rotación en X por `ease * Math.PI * 1.35` y atenuar Y/Z para evitar sacudidas.
4. Ajustar la curva de descenso en Y para que a $t = 0.85$ la pelota ya haya cruzado el borde inferior de la pantalla.
5. Agregar interrupción inmediata: si se detecta un click en `#intro-stage` mientras `animandoCinematica === true`, invocar inmediatamente `cerrarIntro()`.

## Boundaries

- Do NOT touch firmware, Python tools or documentation files.
- Do NOT alter Three.js material roughness, UV planar mapping or lighting colors.
- Do NOT modify the dashboard markup in `<main id="app-main">`.

## Verification

- **Mechanical**: Ejecutar `node -e "const fs = require('fs'); const html = fs.readFileSync('app/index.html', 'utf8'); ..."` para validar sintaxis de JavaScript sin errores.
- **Feel check**:
  - Abrir `http://localhost:8000/app/` y hacer click en `ENTRENAR YA ➔`.
  - Confirmar que la pelota gira con fluidez aristocrática (el texto `DOC` se aprecia claramente girando sin parpadeo).
  - Confirmar que la animación termina nítidamente en menos de 1 segundo y el dashboard queda disponible de inmediato.
  - Hacer un segundo click durante el vuelo y confirmar que salta instantáneamente al dashboard sin trabas.
- **Done when**: La animación dura 950 ms, la rotación no supera $1.5\pi$ radianes y la salida por el borde inferior es continua.
