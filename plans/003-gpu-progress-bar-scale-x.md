# 003 — Acelerar la barra de progreso por GPU mediante `transform: scaleX`

- **Status**: TODO
- **Commit**: 6f5b634
- **Severity**: HIGH
- **Category**: Performance
- **Estimated scope**: 1 file (`app/index.html`), ~15 lines

## Problem

En `app/index.html:525-530`, la barra de progreso de calibración y del modo de test utiliza `transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1)`. Animar la propiedad `width` dispara un ciclo de cálculo de diseño (layout/reflow) y repintado (paint) en el hilo principal del navegador cada vez que se detecta un tiro o se actualiza el porcentaje de calibración.

```css
/* app/index.html:525-527 — current */
.barra-progreso-fill {
  height: 100%;
  background: var(--accent);
  width: 0%;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
}
```

## Target

Modificar la barra de progreso para que use aceleración por GPU mediante la propiedad `transform: scaleX(...)` con `transform-origin: left`, manteniendo `width: 100%`:

```css
/* target CSS */
.barra-progreso-fill {
  height: 100%;
  background: var(--accent);
  width: 100%;
  transform: scaleX(0);
  transform-origin: left center;
  will-change: transform;
  transition: transform var(--dur-base) var(--ease-out), background-color var(--dur-base) var(--ease-out);
}
```

Y en el código JavaScript donde se actualiza el porcentaje:
```javascript
/* target JS */
// En lugar de: el.style.width = pct + '%';
// Usar: el.style.transform = `scaleX(${pct / 100})`;
```

## Repo conventions to follow

- El estilo de barras de progreso se encuentra bajo la sección `/* --- Barra de Progreso --- */`.
- Usa los tokens de movimiento creados en el Plan 002 (`--ease-out`, `--dur-base`).

## Steps

1. En `app/index.html`, actualizar la regla CSS `.barra-progreso-fill` reemplazando `width: 0%;` y la transición de `width` por `width: 100%; transform: scaleX(0); transform-origin: left center; will-change: transform;`.
2. Buscar en el script de `app/index.html` los lugares donde se actualiza el ancho de las barras de progreso (en el modo tutorial o modo test).
3. Reemplazar `.style.width = ...` por `.style.transform = scaleX(...)`.

## Boundaries

- Do NOT change the DOM container `.barra-progreso-wrap`.
- Do NOT alter the semantic background colors (`var(--accent)`, `var(--ok)`).

## Verification

- **Mechanical**: Buscar `barra-progreso-fill` en JavaScript y confirmar que solo se asigne `transform` y no `width`.
- **Feel check**:
  - En el modo Test o Tutorial, simular tiros con el botón `Simulador` y verificar que la barra se mueva de manera 100% fluida a 60/120 fps sin micro-tirones.
- **Done when**: La animación de la barra corre en el compositor de la GPU sin recalcular layout de la página.
