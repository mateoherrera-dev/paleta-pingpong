---
name: DOC · Find Your Edge
description: Sistema visual y de telemetría deportiva para tenis de mesa inteligente
colors:
  primary: "#ff7700"
  neutral-bg: "#070d18"
  neutral-surface: "#0c1527"
  neutral-surface-hover: "#121e36"
  neutral-line: "rgba(255, 255, 255, 0.09)"
  text-primary: "#f8fafc"
  text-muted: "#94a3b8"
  court-blue: "#1e3a8a"
  state-optimal: "#10b981"
  state-warning: "#f59e0b"
  state-critical: "#f43f5e"
  rubber-red: "#dc2626"
  rubber-black: "#111827"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3.5rem)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.45rem"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.01em"
  mono-telemetry:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
    fontSize: "1.75rem"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "normal"
rounded:
  sm: "8px"
  md: "12px"
  lg: "18px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral-bg}"
    rounded: "{rounded.sm}"
    padding: "8px 14px"
  card-stage:
    backgroundColor: "{colors.neutral-surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "16px 18px"
---

# Design System: DOC (Find Your Edge)

## Overview

DOC es la interfaz de telemetría y entrenamiento para tenis de mesa inteligente. Combina el rigor biomecánico del deporte con la claridad de un "entrenador de rincón" (*corner coach*). El sistema visual descansa en tres pilares:
1. **Atmósfera de Cancha Olímpica:** Neutros azul noche profundo inspirados en mesas de torneo ITTF, eliminando el gris monótono y el brillo agresivo de pantallas en clubes deportivos.
2. **Naranja Celuloide como Héroe de Energía:** El color de la pelota reglamentaria de 40 mm guía la acción, los estados activos y el score en vivo.
3. **Fidelidad al Contrato Físico:** Cada elemento digital refleja directamente la orientación y la polaridad física de la paleta (Goma Negra $= -Z$, Goma Roja $= +Z$).

## Colors

### Colores Principales y Neutros
- **Naranja Torneo (`#ff7700`):** Acento identitario primario. Utilizado en botones principales, tabs activas, score técnico y momentos clave de impacto.
- **Azul Cancha Noche (`#070d18`):** Fondo inmersivo que reduce reflejos de iluminación de club y consumo energético en dispositivos móviles.
- **Azul Superficie (`#0c1527`):** Fondo de paneles Dual-Studio (`studio-stage`, `studio-panel`), con variación hover en `#121e36`.
- **Líneas de Contorno (`rgba(255, 255, 255, 0.09)`):** Delimitadores sutiles que definen volumen sin rigidez.

### Colores Semánticos y de Goma
- **Verde Acierto (`#10b981`):** Golpes con score $\ge 75$ pts, rango de ángulo óptimo y estado de conexión BLE activo.
- **Amarillo de Ajuste (`#f59e0b`):** Tiros aceptables pero mejorables ($40-74$ pts) o ruido en clasificación.
- **Rojo Crítico / Alerta (`#f43f5e` / `#dc2626`):** Fallas críticas (cara abierta en topspin), desconexión e identificador de goma de revés ($+Z$).
- **Negro Goma (`#111827`):** Identificador de goma de derecha ($-Z$).

## Typography

- **Fuente de Interfaz:** Pila nativa de precisión (`-apple-system`, `BlinkMacSystemFont`, `SF Pro Display`, `Segoe UI`, `Roboto`).
- **Fuente de Telemetría Numérica:** Pila monoespaciada (`ui-monospace`, `SFMono-Regular`, `Menlo`, `Consolas`) con `font-variant-numeric: tabular-nums` para evitar saltos visuales durante lecturas continuas a 200 Hz.
- **Escala:**
  - *Display (Intro/Hero):* `clamp(2rem, 5vw, 3.5rem)`, peso 900, tracking `-0.03em`.
  - *Título de Golpe:* `1.45rem`, peso 800, tracking `-0.02em`.
  - *Métricas HUD:* `1.75rem`, peso 800 monoespaciado.
  - *Etiquetas HUD:* `0.76rem`, peso 700 mayúsculas, tracking `0.06em`.
  - *Cuerpo y Consejos:* `0.92rem - 0.98rem`, interlineado 1.5.

## Layout

- **Arquitectura Dual-Studio:** Distribución simétrica y balanceada de 2 columnas principales en pantallas amplias (`minmax(340px, 1.25fr) minmax(320px, 1fr)`) que se apila fluidamente en una sola columna en pantallas móviles ($\le 880\text{px}$).
- **Escenario Visual (Izquierda):** Prioriza la física y el visor 3D en tiempo real con iluminación cenital deportiva.
- **Panel Instrumental (Derecha):** Agrupa telemetría 2×2, tarjeta del entrenador DOC y navegación de impactos.
- **Zero Scroll en Modo Entrenamiento:** En pantallas estándar de escritorio y tablets en orientación apaisada, toda la sesión de práctica opera sin scroll vertical para permitir monitoreo a distancia.

## Elevation & Depth

- **Superficies Flat Refinadas:** Las tarjetas utilizan fondos translúcidos satinados con desenfoque de fondo (`backdrop-filter: blur(24px)`), eliminando sombras duras o biseles plásticos.
- **Sombras Direccionales Suaves:** `box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45)` en los contenedores de estudio para despegarlos del fondo con sutileza.
- **Iluminación Cenital de Estadio:** Fondos radiales tenues (`radial-gradient`) que simulan reflectores de cancha sobre el visor 3D y la parte superior del tablero.

## Shapes

- **Métricas y Tarjetas Menores:** Radio de esquina de `12px` (`--radius-md`).
- **Contenedores Principales de Estudio:** Radio de esquina de `16px - 18px` (`--radius-lg`).
- **Badges, Pastillas y Píldoras de Estado:** Radio circular completo `9999px` (`--radius-pill`).
- **Botones Interactivos:** Radio sutil de `8px` (`--radius-sm`).

## Components

- **Botón Primario (`.btn-primary`):** Fondo naranja `#ff7700`, texto de alto contraste en azul noche profundo `#070d18`, borde sutil y elevación neutra.
- **Tarjeta del Entrenador DOC (`.doc-card`):** Superficie con micro-resplandor naranja cálido, avatar circular identitario y selector de voz integrado.
- **Cuadrícula de Telemetría (`.telemetry-grid`):** Matriz de 2×2 celdas con valores en blanco nítido y etiquetas secundarias atenuadas.
- **Visor 3D (`.visor-stage`):** Escenario interactivo Three.js con iluminación de cancha, rotación libre por arrastre y retorno suave a posición de descanso.
- **Dock de Modos (`.dock-container`):** Barra inferior de 3 segmentos con numeración técnica (`01`, `02`, `03`) y pastilla de selección activa.

## Do's and Don'ts

### Do's
- Mantener los valores de telemetría en blanco nítido con monoespaciado tabular.
- Respetar siempre la convención física de ángulo: negativo = cara cerrada hacia la mesa, positivo = cara abierta al techo.
- Asegurar que los consejos de DOC sean concisos, directos y accionables en mesa.
- Garantizar contraste suficiente ($\ge 4.5:1$) en todos los botones y etiquetas clave para visibilidad a 2 metros de distancia.

### Don'ts
- **No pintar cada celda de un color fluorescente diferente:** Evitar arcoíris innecesarios que distraigan de la pelota en juego.
- **No usar sombras de neón sin compensación directional:** Evitar halos de resplandor cero-offset (`0 0 16px`) en fondos oscuros.
- **No usar jerga académica en la interfaz:** No escribir "clasificador densamente conectado", "red neuronal", ni "cuaternión de orientación" de cara al jugador.
- **No cortar abruptamente la perspectiva de la mesa:** Mantener la sensación de cancha continua e infinita.
