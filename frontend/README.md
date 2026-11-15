# TimeScope frontend

The React/TypeScript interface for TimeScope provides coordinate search, a fixed SPHEREx observation viewer, chronological playback, paired comparisons, scientific metadata, a time–wavelength graph, target presets and HTML evidence export.

## Development

From the repository root, follow [SETUP.md](../SETUP.md) to prepare the backend. Then run:

```bash
npm --prefix frontend ci
npm --prefix frontend run build
npm --prefix frontend run lint
.venv/bin/python -m backend
```

Open http://localhost:8000. For frontend development, use `npm run dev` from this directory; see [vite.config.ts](vite.config.ts) for proxy settings.

## Browser checks

With the backend running on port 8000:

```bash
npx playwright install chromium
npx playwright test --workers=1
```

See the [project README](../README.md) for scientific limitations, data attribution, verified results and deployment details. This frontend uses the standard Vite React template as its starting point; upstream licenses are retained.
