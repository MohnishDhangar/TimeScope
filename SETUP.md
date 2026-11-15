# TimeScope local setup

This is the bootstrap environment for the implementation, not a completed application. Dependency installation failed in the agent terminal on November 14, 2026; it also could not resolve IRSA's hostname. Update: installation subsequently succeeded after network access was enabled, using the existing Python 3.14.7 virtual environment. pip check and dependency imports passed. Exact installed versions are in requirements-resolved.txt; application-level compatibility and live data retrieval still need validation. Requirements are intentionally unpinned until a successful installation and test run establishes a reproducible lock.

## Required tools

- Python 3.12 recommended for the initial scientific environment, with pip and venv. This is a project choice, not a claim that other Python versions are unsupported.
- Node.js and npm: existing environment reports Node 26.10.0 and npm 12.1.0; do not reinstall without a compatibility failure.
- Git, a modern browser, and an editor.
- Network access to PyPI, npm, IRSA and documentation sites.

## Python

From this directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check
```

Use the existing compatible Python executable if python3.12 is unavailable; verify package installation before continuing. The current `.venv` was created with the environment's `python` command, not a verified Python 3.12 executable.

Runtime packages: FastAPI, Uvicorn and Pydantic for the API; NumPy and SciPy for arrays and numerical operations; Astropy for FITS, coordinates and time; Astroquery for archive discovery; reproject for celestial alignment; Pillow for previews; HTTPX for bounded HTTP access. pytest is development-only. SQLite and concurrent.futures are supplied by Python; do not install a package named sqlite3.

## Frontend

When no frontend exists yet:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @playwright/test
npx playwright install chromium
```

The template installs React, React DOM, TypeScript, Vite and its React integration. Keep package-lock.json. Canvas, browser fetch and CSS need no packages. Browser dependencies on Linux may require OS installation; follow Playwright's reported instructions rather than assuming administrative access.

## Data

Use the IRSA notebooks to discover and retrieve small SPHEREx cutouts. First obtain two distinct acquisition times for one field; retain all returned FITS extensions, archive metadata and retrieval provenance. Then expand to a bounded sequence. Do not download the whole survey, Gaia catalog or WISE catalog. No real observations have been downloaded yet.

- https://irsa.ipac.caltech.edu/Missions/spherex.html
- https://caltech-ipac.github.io/irsa-tutorials/spherex/
- https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/

Cache under data/ outside version control. Keep small provenance manifests in source. Reserve roughly 5–10 GB initially for environments, browser tooling and data cache; this is a planning allowance, not a measured download size.

## Optional packages

- pyvo: direct TAP/VO access if required by the cutout notebook.
- jupyterlab, ipykernel, matplotlib: run and inspect notebooks interactively.
- firefly-client: follow the tutorial's optional Firefly visualization path.
- photutils: later source measurement/detection.
- Aladin Lite: later sky-context viewer, subject to license review.
- Tailwind CSS: optional styling; plain CSS is sufficient initially.

## Services, not local downloads

Need a source repository account and, for deployment, a static frontend host and a Python-capable backend host. One Python host can alternatively serve the frontend build too. Hosting provider and plan are not yet selected; verify storage, memory, timeouts, HTTPS and public access before purchase. Docker is optional unless the chosen host requires it. No paid NASA API key is part of the proposed public archive workflow. No LLM service, Redis, PostgreSQL, GPU runtime or object-storage account is required for the first local milestone.
