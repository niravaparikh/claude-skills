# Comparison checklist

Run per matched screen, per breakpoint, per theme mode. Record prototype value, live value, and evidence.

## Before comparing (see `dynamic-content.md`)
- Same role, same screen state, same breakpoint, same theme mode on both sides; data parity agreed with the user
- Collapsed controls opened (dropdowns, tabs, accordions, toggles) and captured
- Full text captured, not truncated
- Each difference classified S / D / I / T / ST / C / P / E; only S is rated, every class is listed and tagged (see SKILL.md "Dynamic content")
- Live wording searched in the prototype source for self-contradiction (P)

Everything below applies to static (S) content and tokens. For data, identity, time and state compare format and styling for severity; the value difference itself is listed as dynamic, never rated.

## Every element, every page (the inventory)
- Run `extract-inventory.js` on the full page, scrolled content included, repeating with OFFSET until `next` is null
- Also capture: hidden-until-interaction UI (menus, modals, drawers, tooltips, toasts, dropdown options, tab panels, accordions, row actions, validation messages) by triggering each one, then re-running the inventory in that state
- `diff-extracts.py` COVERAGE must add up on both sides; every element lands in paired, weak-paired, only-in-prototype or only-in-live. A page with a coverage mismatch or an incomplete inventory is not "compared"
- Every only-in-prototype and only-in-live element gets a disposition: finding, Needs confirmation (conditional), or excluded with its class. None are left unlisted

## Look and feel
- Font family (full computed stack), size, weight, line-height, letter-spacing, text-transform, colour
- Colours: text, background, border, icon fill, link, placeholder, selection; compare as computed `rgb()` and hex
- Spacing: margin, padding, gap between siblings; container max-width and alignment
- Layout: element order, grid/flex structure, alignment, element sizes, overflow, z-order
- Borders, radius, shadows, opacity, gradients, dividers
- Images, icons, logos: presence, size, aspect ratio, source type (svg/png), alt text
- Page chrome: header, footer, nav, sidebars, favicon/title

## Components and behaviour
- Buttons: default, hover, focus, active, disabled, loading; cursor; click result; double-click guard
- Links: colour states, underline, target, visited
- Forms: label placement, required markers, placeholder, input states, validation message text/timing/colour, tab order, autofocus, submit behaviour
- Menus, dropdowns, modals, tabs, accordions, tooltips, toasts: open/close, escape key, focus trap, backdrop
- Tables/lists: header style, row hover, sorting, pagination, empty state
- Transitions and animations: duration, easing, what moves
- Loading, empty and error states

## Responsive
- At each user-supplied width: layout reflow, hidden/shown elements, nav collapse, font scaling, touch target size, horizontal scroll

## Accessibility and content
- Text copy, capitalisation, punctuation, labels, microcopy
- Colour contrast of text and controls (compute ratio)
- Keyboard: tab order, visible focus ring, operable without a mouse
- Semantics: headings order, landmarks, button vs link, aria-labels, alt text, lang attribute

## Theme (see `theme-pass.md`)
- Token sets, page drift, declared custom properties, theme signals
- Each shared component type once at theme level
- Each theme mode the user confirmed exists, switched by the method the user described
