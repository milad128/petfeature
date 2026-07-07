---
name: design-system-tokens
description: CSS custom properties, typography, and spacing conventions shared across all petfeature .dc.html design files
metadata:
  type: project
---

## Color tokens

Light theme (`[data-theme="light"]`):
- `--bg:#faf9f7` — page background (warm off-white)
- `--surface:#ffffff` — card/widget background
- `--surface-2:#fbfaf8` — form background (slightly tinted)
- `--border:#e8e2db` — borders and dividers
- `--text:#1c1917` — body text
- `--muted:#78716c` — secondary/meta text
- `--accent:#c2410c` — primary brand color (rust/orange)
- `--accent-bg:#fff7ed` — accent tint (pill backgrounds, quote fills)
- `--accent-bd:#fde0c8` — accent border (selection, notices)
- `--shadow:0 8px 32px rgba(0,0,0,0.08)`

Dark theme (`[data-theme="dark"]`):
- `--bg:#0d0f12`
- `--surface:#15181e`
- `--surface-2:#11141a`
- `--border:rgba(255,255,255,.09)`
- `--text:#eceef1`
- `--muted:#9aa1aa`
- `--accent:#f0834e`
- `--accent-bg:rgba(240,131,78,.12)`
- `--accent-bd:rgba(240,131,78,.28)`
- `--shadow:0 18px 48px rgba(0,0,0,0.45)`

## Typography

- Font: `'Vazirmatn'` (Google Fonts, weights 300/400/500/600/700), fallback `system-ui, Tahoma, sans-serif`
- Body: `font-size` base, `line-height:1.8`, `direction:rtl`, `-webkit-font-smoothing:antialiased`
- Section labels: `font-size:12.5px; font-weight:600; color:var(--accent); letter-spacing:.04em`
- Section headings (comments, ratings): `font-size:1.05rem; font-weight:700`
- Muted meta text: `font-size:.78rem–.88rem; color:var(--muted)`

## Layout

- Book detail max-width: `1100px`; blog post max-width: `720px`
- Book detail grid: `grid-template-columns:280px 1fr; gap:44px`
- Aside is sticky: `position:sticky; top:100px`
- Container padding: `34px 24px 80px`
- Section spacing: `margin-bottom:36px` between content sections

## Component border-radius scale

- Pills/tags: `border-radius:20px`
- Buttons: `border-radius:9px`
- Cards (small): `border-radius:10px`
- Cards (standard): `border-radius:12px`
- Widgets (rating, form): `border-radius:14px`
- Cover image: `border-radius:12px`

## Quotes

- `background:var(--accent-bg); border-right:3px solid var(--accent); border-radius:0 10px 10px 0; padding:16px 20px`
- Note: `border-right` not `border-left` — RTL convention, accent border on the reading-start side

**Why:** All .dc.html files share this token set. Maintaining consistency here is critical for theme switching to work correctly.
