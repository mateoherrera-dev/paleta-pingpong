# 002 — Definir tokens globales de movimiento y eliminar `transition: all`

- **Status**: TODO
- **Commit**: 6f5b634
- **Severity**: HIGH
- **Category**: Performance / Cohesion & tokens
- **Estimated scope**: 1 file (`app/index.html`), ~25 lines CSS

## Problem

En `app/index.html:120, 145, 193, 307, 443, 499`, múltiples componentes interactivos de alta frecuencia (`button`, `.tab-pill`, `.chip-btn`, `.dot-status`, `.critique-card`, `.visor-badge-cara`) utilizan `transition: all`. Cuando se interactúa con estos controles o se reciben golpes continuos de telemetría a 1-2 Hz, el navegador interpola propiedades que no están en la GPU (como border-width, padding o layout), provocando recálculos de estilo en medio del bucle 3D de Three.js. Además, se usan duraciones dispares y curvas genéricas débiles (`ease`).

```css
/* app/index.html:120 — current */
.dot-status { transition: all 0.3s ease; }

/* app/index.html:145 — current */
button { transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1); }

/* app/index.html:193 — current */
.tab-pill { transition: all 0.18s ease; }

/* app/index.html:443 — current */
.critique-card { transition: all 0.2s ease; }
```

## Target

Declarar en `:root` los tokens canónicos de movimiento según las especificaciones de Emil Kowalski:
```css
/* target tokens in :root */
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--dur-fast: 140ms;
--dur-base: 220ms;
```

Reemplazar `transition: all` por las propiedades exactas que cambian en cada selector:
```css
/* target selectors */
.dot-status {
  transition: background-color var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out);
}
button {
  transition: background-color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out);
}
.tab-pill {
  transition: background-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out), box-shadow var(--dur-fast) var(--ease-out);
}
.critique-card {
  transition: background-color var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out), color var(--dur-base) var(--ease-out);
}
.chip-btn {
  transition: background-color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out);
}
.visor-badge-cara {
  transition: transform var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out);
}
.visor-badge-cara:active {
  transform: scale(0.97);
}
```

## Repo conventions to follow

- Las variables de diseño viven en `:root` dentro de `<style>` en `app/index.html` (líneas 10–32).

## Steps

1. En `app/index.html`, agregar las 4 variables de movimiento (`--ease-out`, `--ease-in-out`, `--dur-fast`, `--dur-base`) al bloque `:root`.
2. Actualizar `.dot-status` eliminando `transition: all 0.3s ease;` y usando las propiedades específicas.
3. Actualizar `button` reemplazando `transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);`.
4. Actualizar `.tab-pill` y `.chip-btn`.
5. Actualizar `.critique-card` y `.visor-badge-cara`.
6. Añadir el estado `:active` con `transform: scale(0.97)` en `.visor-badge-cara`.

## Boundaries

- Do NOT alter colors, border radii, or box shadows.
- Do NOT remove `:active` scaling states on buttons.

## Verification

- **Mechanical**: Grep para confirmar que no quede ningún `transition: all` en `app/index.html`.
- **Feel check**:
  - Tocar o clickear las pestañas de navegación (Entrenamiento / Test / Live). La respuesta debe ser inmediata, sin retardo flotante.
  - Tocar el switch de caras (Roja / Negra) en el visor 3D y comprobar el micro-resorte en `:active`.
- **Done when**: Ninguna regla CSS en `app/index.html` usa `transition: all` y todos los componentes interactivos usan los tokens `--ease-out` / `--dur-fast`.
