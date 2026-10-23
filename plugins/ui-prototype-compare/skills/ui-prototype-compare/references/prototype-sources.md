# Reading each prototype type

The prototype must stay at its original path. Never copy it into this repo.

## HTML/CSS/JS
- Try opening it in the Playwright MCP browser via a `file://` URL.
- If the browser blocks `file://`, serve the prototype's own folder read-only on a localhost port (for example `python -m http.server <port>` run with that folder as working directory), use `http://localhost:<port>/`, and stop the server when done. Tell the user you are doing this.
- Extract computed styles with `extract-styles.js` and compare exactly.

## Images, screenshots, PDF
- Read the files directly (PDFs by page range). Describe visible fonts, colours, spacing and layout.
- Values read from pixels are estimates; label them "estimated from image" and never claim exactness. Behaviour cannot be verified.

## Figma export or spec
- Read the exported assets or token/spec files (JSON, CSS variables, style guides). Treat explicit token values as exact; treat anything inferred from rendered images as estimated.
- If the export format is unfamiliar, ask the user what the files contain before proceeding.

## Mixed
- If several types are provided, say which source you used for each finding.
