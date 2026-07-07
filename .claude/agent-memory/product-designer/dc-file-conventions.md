---
name: dc-file-conventions
description: Conventions for .dc.html design component files used in petfeature redesign — structure, DCLogic script, template syntax
metadata:
  type: project
---

## File structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" ...>
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <!-- fonts + <style> block with CSS variables and media queries -->
</helmet>

<div data-theme="{{ theme }}" data-screen-label="Screen Name" style="...">
  <!-- all page markup with inline styles -->
</div>
</x-dc>

<script type="text/x-dc" data-dc-script data-props="{ JSON-encoded prop schema }">
class Component extends DCLogic {
  state = { ... };
  renderVals() { return { ... }; }
}
</script>
</body>
</html>
```

## Template syntax

- `{{ variableName }}` — renders a value from `renderVals()`
- `onClick="{{ handlerName }}"` — event handler reference
- `onMouseEnter="{{ handlerName }}"` / `onMouseLeave="{{ handlerName }}"` — hover handlers
- `ref="{{ refName }}"` — attach a React ref to an input/textarea
- `style-hover="..."` — hover style (dc-specific, not standard CSS)

## Conditional rendering

```html
<sc-if value="{{ booleanVal }}" hint-placeholder-val="{{ false }}">
  <!-- shown when value is true -->
</sc-if>
```

- `hint-placeholder-val` sets the default preview state (true = show in static preview, false = hide)

## List rendering

```html
<sc-for list="{{ itemsArray }}" as="item" hint-placeholder-count="2">
  <!-- template; use {{ item.field }} for properties -->
</sc-for>
```

- `hint-placeholder-count` controls how many placeholder items show in static preview

## DCLogic class patterns

- `state = { ... }` — reactive state
- `renderVals()` — returns object of all template bindings; called on every render
- `componentDidMount()` / `componentDidUpdate()` — lifecycle hooks (used for DOM-dependent operations like star coloring)
- `React.createRef()` in constructor for input refs
- `this.setState(s => ({ ... }))` for functional state updates
- `clearTimeout(this._t); this._t = setTimeout(...)` pattern for auto-dismissing notices

## data-props schema (in the script tag)

```json
{
  "$preview": { "width": 1180, "height": 1500 },
  "theme": {
    "editor": "enum",
    "options": ["light", "dark"],
    "default": "dark",
    "tsType": "'light' | 'dark'"
  }
}
```

- `$preview` controls the canvas size in the design tool
- Book detail pages: width 1180; blog post page: width 900
- Default theme is `"dark"` in all existing files

## RTL-specific inline style notes

- All containers: `direction:rtl` on `body` (inherited, not repeated on every element)
- Email inputs: `direction:ltr; text-align:right` — email addresses are LTR characters but should align to the RTL reading edge
- Quote borders: `border-right` not `border-left` — the accent border goes on the right (reading-start) side in RTL
- Breadcrumb separator: `‹` (left-pointing) since RTL reads right-to-left, parent › child reads as parent ‹ child visually
- Arrow in submit button: `←` (leftward) signals "proceed/submit" in RTL — the reading direction forward is left

**Related:** [[design-system-tokens]] [[book-engagement-pattern]]
