# 004 — Soporte de accesibilidad `prefers-reduced-motion`

- **Status**: TODO
- **Commit**: 6f5b634
- **Severity**: MEDIUM
- **Category**: Accessibility
- **Estimated scope**: 1 file (`app/index.html`), ~20 lines

## Problem

En `app/index.html`, no existe ninguna regla `@media (prefers-reduced-motion: reduce)`. Los usuarios que tienen activada la reducción de movimiento en su sistema operativo por trastornos vestibulares o mareo por movimiento son sometidos involuntariamente al zoom macro 3D y a la rotación de topspin.

## Target

1. Agregar en CSS la media query para desactivar desplazamientos bruscos y conservar únicamente desvanecimientos suaves de opacidad:
```css
/* target CSS */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  #intro-stage {
    transition: opacity 200ms ease, visibility 200ms ease !important;
  }
}
```

2. En JavaScript, consultar `window.matchMedia('(prefers-reduced-motion: reduce)').matches`:
```javascript
/* target JS en dispararIntroCinematica */
if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  cerrarIntro();
  return;
}
```

## Repo conventions to follow

- Las media queries de temas o accesibilidad se ubican al final del bloque `<style>`.

## Steps

1. En `app/index.html`, agregar el bloque `@media (prefers-reduced-motion: reduce)` en los estilos.
2. En la función `dispararIntroCinematica()`, chequear si la preferencia reducida está activa para saltar directo a `cerrarIntro()` de forma instantánea.

## Boundaries

- Do NOT remove opacity fades that provide comprehension feedback.
- Do NOT alter functional colors or typography.

## Verification

- **Mechanical**: Emular `prefers-reduced-motion: reduce` en DevTools (panel Rendering -> Emulate CSS media feature prefers-reduced-motion).
- **Feel check**:
  - Al hacer click en `ENTRENAR YA ➔` con la preferencia activa, la pantalla naranja simplemente se desvanece en 200 ms hacia el dashboard sin giros ni parábolas de cámara.
- **Done when**: La app responde adecuadamente a las preferencias de accesibilidad del usuario sin provocar vértigo.
