# NBS-1 "Data Voyager" Visual Blueprint — Integration Guide

**NetworkBuster Aerospace Division · Rev 1.0**

---

## Overview

`spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html` is a self-contained,
interactive SVG/CSS blueprint for the NBS-1 "Data Voyager" spacecraft.  
It requires **no build tools, no frameworks, and no external dependencies** — open it
directly in any modern browser or embed it in your project.

---

## Quick Start

### 1. Open Standalone

```bash
# From the repository root
open spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html
# or
start spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html   # Windows
xdg-open spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html # Linux
```

### 2. Serve Locally

```bash
# Python (any platform)
python -m http.server 8080
# then visit: http://localhost:8080/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html

# Node.js (npx)
npx serve .
```

---

## Embedding in an Existing HTML Page

### Option A — `<iframe>` (recommended, zero style conflicts)

```html
<iframe
  src="/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html"
  width="100%"
  height="800"
  style="border:none; border-radius:8px;"
  title="NBS-1 Data Voyager Interactive Blueprint"
  loading="lazy">
</iframe>
```

### Option B — Inline `<object>` tag

```html
<object
  data="/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html"
  type="text/html"
  width="100%"
  height="800">
  <p>Your browser does not support embedded objects.
     <a href="/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html">
       Open blueprint
     </a>
  </p>
</object>
```

### Option C — JavaScript Dynamic Embed

```javascript
const container = document.getElementById('blueprint-container');
const iframe = document.createElement('iframe');
iframe.src = '/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html';
iframe.style.cssText = 'width:100%;height:800px;border:none;border-radius:8px;';
iframe.title = 'NBS-1 Data Voyager Interactive Blueprint';
iframe.loading = 'lazy';
container.appendChild(iframe);
```

---

## Embedding the SVG Directly

The blueprint contains three inline SVG diagrams (side view, front view, top view).
You can extract an individual SVG and paste it directly into your page.

1. Open `NBS-1-VISUAL-BLUEPRINT.html` in a text editor.
2. Locate the `<svg id="view-side" …>` block (or `view-front` / `view-top`).
3. Copy the entire `<svg>…</svg>` element.
4. Paste it into your HTML — the SVG is self-styled via `<style>` inside the file
   and CSS custom properties (`--accent`, `--bg`, etc.), so you can override them:

```html
<style>
  /* Override blueprint colours to match your theme */
  svg.blueprint {
    --accent: #ff6b35;   /* change highlight colour */
    --bg: #ffffff;
  }
</style>

<!-- paste extracted SVG here -->
```

---

## Vercel / Static Hosting

The file is already tracked in the repository and will be deployed automatically by Vercel
as a static asset.  Access it at:

```
https://<your-preview-url>/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html
```

No additional `vercel.json` configuration is required.

---

## React / Next.js Integration

```jsx
// components/SpaceshipBlueprint.jsx
export default function SpaceshipBlueprint({ height = 800 }) {
  return (
    <iframe
      src="/spaceship-3d-blueprints/spacecraft/NBS-1-VISUAL-BLUEPRINT.html"
      width="100%"
      height={height}
      style={{ border: 'none', borderRadius: 8 }}
      title="NBS-1 Data Voyager Interactive Blueprint"
      loading="lazy"
    />
  );
}
```

```jsx
// pages/spacecraft.jsx  (or app/spacecraft/page.jsx for App Router)
import SpaceshipBlueprint from '../components/SpaceshipBlueprint';

export default function SpacecraftPage() {
  return (
    <main>
      <h1>NBS-1 "Data Voyager"</h1>
      <SpaceshipBlueprint height={900} />
    </main>
  );
}
```

> **Note:** Place `NBS-1-VISUAL-BLUEPRINT.html` inside the Next.js `public/` folder
> (e.g. `public/blueprints/NBS-1-VISUAL-BLUEPRINT.html`) and update the `src`
> path accordingly.

---

## Interactive Features

| Feature | How to Use |
|---------|-----------|
| **View switching** | Click **Side View / Front View / Top View** tabs above the SVG |
| **Section details** | Click any coloured section on the blueprint to show specs in the right panel |
| **Systems status** | Animated progress bars in the right panel show live-style readings |
| **Responsive layout** | The layout stacks vertically on screens narrower than 860 px |

---

## Accessibility

- All three SVG diagrams have `role="img"` and descriptive `aria-label` attributes.
- Interactive sections have `aria-label` attributes for screen readers.
- Colour contrast meets WCAG AA for text on the dark background.

---

## Customisation Reference

All colours are defined as CSS custom properties at the top of the file:

| Variable | Default | Purpose |
|----------|---------|---------|
| `--bg` | `#0a0e1a` | Page background |
| `--panel` | `#0d1526` | Card/panel background |
| `--accent` | `#00d4ff` | Primary highlight (cyan) |
| `--accent2` | `#7b4fff` | Secondary highlight (purple) |
| `--text` | `#c8d8f0` | Body text |
| `--dim` | `#4a6080` | Muted text / dimension lines |

---

## File Reference

```
spaceship-3d-blueprints/
├── spacecraft/
│   ├── NBS-1-SPECS.md               ← Full technical specification
│   └── NBS-1-VISUAL-BLUEPRINT.html  ← Interactive visual (this file)
├── moonbase-alpha/
├── orbital-station/
├── INTEGRATION.md                   ← You are here
└── README.md
```

---

**Copyright © 2026 NetworkBuster Aerospace Division**  
*"Delivering Data to the Final Frontier"*
