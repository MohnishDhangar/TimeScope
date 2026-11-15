# Local setup

TimeScope is a React/TypeScript/Vite frontend served by a scientific FastAPI backend. Three genuine SPHEREx examples are bundled. Live searches require working NASA/IPAC IRSA services.

## Environment

The verified local environment on November 15, 2026 is Python 3.14.7, Node 26.10.0, npm 12.1.0 on Linux. The successful production Docker build uses Python 3.14 and a Node 24 build stage. Do not replace pinned versions without verifying compatibility. Exact Python dependencies: `requirements-resolved.txt`; frontend: `frontend/package-lock.json`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-resolved.txt
.venv/bin/python -m pip check
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m backend
```

Open http://localhost:8000. `PORT` is read by the backend, which binds 0.0.0.0; Cloud Run supplies its reserved PORT itself. `VITE_SHOWCASE_ONLY` must be false or unset for a full build. Do not install Python packages into the system interpreter.

## Tests

```sh
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest -q
npm --prefix frontend run lint
npm --prefix frontend run build
cd frontend
npx playwright install chromium
npx playwright test --workers=1
```

Keep the backend running on port 8000 for Playwright. Browser dependencies depend on the host; follow the supported Playwright installation instructions if Chromium cannot start. Tests use synthetic failure fixtures and preserved real previews; ordinary tests do not query NASA.

## Runtime settings

| Setting | Default / behavior |
|---|---|
| `TIMESCOPE_DATA_DIR` | `data` beneath this checkout; disposable live files |
| `TIMESCOPE_MAX_CACHE_MB` | 512 MiB aggregate file budget |
| `TIMESCOPE_SESSION_TTL_SECONDS` | 21600 seconds for inactive live sessions |
| `TIMESCOPE_MAX_JOBS_PER_HOUR` | 12 new jobs globally; retained exact-query reuse exempt |
| `TIMESCOPE_DISCOVERY_BUDGET_S` | 90 seconds maximum; public API further caps at 60 |

Keep scientific originals outside disposable runtime storage. Do not commit runtime files, virtual environments, credentials or raw FITS. Bundled PNGs/manifests and the historical exact-query metadata snapshot are intentional tracked artifacts.

A healthy local server is not proof of IRSA availability. Open a bundled field for a network-independent viewer check. For genuine live-search verification, retain the exact query, session ID, discovery method, metadata timestamp, per-frame FITS-cache flags, failures and elapsed time. Never use a different example as the result of a failed search.

Cloud deployment instructions are maintained only in [CLOUD-DEPLOYMENT.md](docs/CLOUD-DEPLOYMENT.md). Current release evidence is in [FINAL-STATUS.md](docs/FINAL-STATUS.md). A clean-clone installation has not been reproduced in this repair session; the existing environment and actual Cloud Build are verified separately.
