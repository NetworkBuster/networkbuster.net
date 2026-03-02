# Integration Guide — Spaceship 3D Blueprint Visual Example

## Introduction

This guide explains how the **NBS-1 "Data Voyager"** visual blueprint example is structured and how to embed or extend it within the NetworkBuster project or any web application.

The visual example (`spacecraft/NBS-1-VISUAL-BLUEPRINT.html`) is a self-contained, zero-dependency HTML file that renders:

- **Annotated side-profile blueprint** — all major sections labelled with dimension lines
- **Fuselage cross-section** — Station 18 interior layout
- **Animated isometric 3D schematic** — CSS `perspective` + `transform-style: preserve-3d` rotation
- **Propulsion system schematic** — ME-50 methalox engine block diagram
- **Avionics & network architecture** — block diagram linking flight computers to subsystems
- **Mission timeline** — six-phase visual timeline from launch to splashdown

---

## Architecture Overview

```
spaceship-3d-blueprints/
├── INTEGRATION.md              ← You are here
├── README.md                   ← Space infrastructure overview
├── spacecraft/
│   ├── NBS-1-SPECS.md          ← Full technical specifications (text)
│   └── NBS-1-VISUAL-BLUEPRINT.html  ← Interactive visual blueprint
├── moonbase-alpha/
│   └── README.md
└── orbital-station/
    └── CLOUD-ONE-SPECS.md
```

### Components in the visual file

| Section | Technology | Description |
|---------|-----------|-------------|
| Blueprint grid background | CSS `background-image` repeating gradients | Simulates engineering graph paper |
| Side-profile schematic | Inline SVG with `<path>`, `<rect>`, dimension lines | Annotated 2D blueprint |
| Cross-section view | Inline SVG | Circular fuselage cross-section at Station 18 |
| Isometric 3D schematic | SVG + CSS `animation` (`rotateY`/`rotateX`) | Simulated 3D perspective, pausable on hover |
| Engine schematic | Inline SVG | Methalox turbopump → combustion → nozzle flow |
| Avionics diagram | Inline SVG | Triple-redundant FC voting bus → subsystems |
| Mission timeline | SVG thumbnails in a CSS Grid | Phase-by-phase visual strip |
| Animated engine flames | CSS `@keyframes` `opacity`/`scaleY` | Exhaust plume pulse effect |

---

## Integration Steps

### 1 — Standalone usage

Open `spacecraft/NBS-1-VISUAL-BLUEPRINT.html` directly in any modern browser.
No build step, no server, no external dependencies required.

```bash
# From the repository root
open spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html
# or
xdg-open spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html
```

### 2 — Served via the NetworkBuster Express server

The existing `server.js` already serves static files. Copy or symlink the blueprint file
into the `public/` or `web-app/` folder (whichever `express.static` points to):

```bash
cp spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html \
   web-app/nbs1-blueprint.html
```

Then visit `http://localhost:3001/nbs1-blueprint.html`.

### 3 — Embed inside the React app

Add a new route in `src/App.jsx` for the blueprint iframe view:

```jsx
// src/App.jsx — add to nav list
<li>
  <a href="/blueprint" onClick={(e) => handleNavigation(e, 'blueprint')}>
    Blueprint
  </a>
</li>

// Render it in <main>
{currentPage === 'blueprint' && (
  <iframe
    src="/nbs1-blueprint.html"
    title="NBS-1 3D Blueprint"
    style={{ width: '100%', height: '90vh', border: 'none' }}
  />
)}
```

### 4 — Extend with additional spacecraft

To add a blueprint for a new spacecraft (e.g. the Cloud One Station):

1. Create `orbital-station/CLOUD-ONE-VISUAL-BLUEPRINT.html` following the same
   self-contained HTML pattern used in `NBS-1-VISUAL-BLUEPRINT.html`.
2. Use the same CSS custom properties (`:root` variables) to maintain the
   blueprint design language.
3. Link to the new file from `orbital-station/CLOUD-ONE-SPECS.md`.

---

## Design System

All visual styles are driven by CSS custom properties at the top of the file:

| Variable | Value | Usage |
|----------|-------|-------|
| `--bp-bg` | `#0a1628` | Page background |
| `--bp-grid` | `#1a3a6e` | Grid lines, subtle dividers |
| `--bp-line` | `#4da8ff` | Primary structural lines |
| `--bp-accent` | `#00d4ff` | Highlighted components, labels |
| `--bp-white` | `#c8e4ff` | Body text |
| `--bp-dim` | `#5a8ab5` | Secondary / dimmed text |
| `--bp-orange` | `#ff9f40` | Fuel / warning indicators |
| `--bp-red` | `#ff5a5a` | Critical / ignition indicators |
| `--bp-green` | `#4dff91` | Avionics / data systems |

---

## Accessibility

- All `<svg>` elements carry `aria-label` attributes describing their content.
- Animations respect `prefers-reduced-motion` — add the following snippet to
  honour that preference if needed:

```css
@media (prefers-reduced-motion: reduce) {
  .spacecraft-3d { animation: none; }
  .engine-flame   { animation: none; }
  .glow-svg       { animation: none; }
}
```

---

## References

- **Technical specifications:** `spacecraft/NBS-1-SPECS.md`
- **Infrastructure overview:** `README.md`
- **Artemis L-system integration pattern** — the visual example follows the same
  structure described for the Artemis demo: a renderer is initialised, a data
  source (spacecraft specs) is connected to it, and the output is rendered as an
  annotated diagram. In this project the "renderer" is inline SVG driven by CSS
  custom properties, and the "data source" is `NBS-1-SPECS.md`.
  External reference (may become unavailable):
  [nasa-waste-calc INTEGRATION.md](https://github.com/Cleanskiier27/nasa-waste-calc/blob/main/examples/artemis_demo/INTEGRATION.md)

---

*"Delivering Data to the Final Frontier"*

**NetworkBuster Aerospace Division · © 2026**
