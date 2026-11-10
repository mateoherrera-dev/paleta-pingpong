# Planes de Mejora de Animaciones y Movimiento · DOC

Generados a partir de la auditoría de diseño e ingeniería de animación ([`improve-animations`](file:///C:/Users/tomas/.gemini/config/skills/improve-animations/SKILL.md)).

## Tabla de Planes

| # | Plan | Severidad | Categoria | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **001** | [Calibrar rotacion, duracion y resolucion de la cinematica 3D](001-cinematica-pelota-rotacion-y-duracion.md) | **HIGH** | Easing & duration / Physicality | `DONE` |
| **002** | [Definir tokens globales de movimiento y eliminar `transition: all`](002-motion-tokens-y-eliminar-transition-all.md) | **HIGH** | Performance / Cohesion & tokens | `DONE` |
| **003** | [Acelerar la barra de progreso por GPU mediante `transform: scaleX`](003-gpu-progress-bar-scale-x.md) | **HIGH** | Performance | `DONE` |
| **004** | [Soporte de accesibilidad `prefers-reduced-motion`](004-prefers-reduced-motion-accessibility.md) | **MEDIUM** | Accessibility | `DONE` |

## Orden de Ejecución Recomendado

1. **Plan 001**: Resuelve inmediatamente el feedback visual crítico (frenar la rotación estroboscópica a altísima velocidad y acortar la duración a 950 ms).
2. **Plan 002**: Declara las variables canónicas de movimiento (`--ease-out`, `--dur-fast`) y limpia los 6 lugares con `transition: all`.
3. **Plan 003**: Acelera la barra de progreso por GPU usando los tokens declarados en el Plan 002.
4. **Plan 004**: Garantiza accesibilidad y salida suave para usuarios con reducción de movimiento activada.
