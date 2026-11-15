# Final acceptance test report

Tested application source: `2ec672dabb10bd2a47dad442e1c9423196af4950`; docs baseline `1f7f435`. Acceptance started 2026-11-15T16:48:45Z. Dependency versions unchanged.

| Command | Result |
|---|---|
| Existing venv python -m pytest -q | 121 passed, 0 failed/skipped; one Starlette/httpx deprecation warning; 2.25 s |
| npm --prefix frontend ci | Passed; clean installation from existing lockfile |
| npm --prefix frontend run build | Passed; 23 modules; 187 ms Vite phase |
| npm --prefix frontend run lint | Passed |
| npx playwright test --workers=1 --reporter=line | Initial run: 25 browser failures from local server absent, one logic pass. Started documented backend and reran: 26 passed, 0 failed/skipped; 11.8 s |

26 checks comprise 25 Chromium scenarios and one metadata-logic test. Coverage includes all three genuine bundles, API-unavailable operation, play/pause/wrapping, blink/pair blink, synchronized comparison/pan/zoom, image interpolation, graph selection, evidence with embedded previews, view restoration, navigation, error/Retry payloads, historical timestamps and four fixed-viewer viewport scenarios. Synthetic errors never hit NASA.

Fresh actual deployed screenshots are in screenshots/final/: search, library, viewer, comparison, 1366×768 laptop and 390×844 mobile; desktop captures use 1920×1080. The full public suite is rerun separately and recorded in final-acceptance.md. The initial missing-server failure is a test-environment failure, not hidden as an application pass.

Scientific checksum/wavelength reconstruction was reproduced during the immediately preceding integration acceptance; current package does not claim it was repeated a second time here. Software success is not scientific detection validation.

Public rerun: 26 passed, 0 failed/skipped in 1.4 minutes. Small CSS-only final corrections remove a stale teal panel and improve graph-axis readability; the final freeze build/regression is recorded with release identity after deployment.

Final transport repair raises the per-read ceiling from 20 to 35 seconds, bounded by remaining discovery time, to accommodate observed successful 24–25 s responses. Shared discovery/job budgets and retry caps remain unchanged. Synthetic transport regression added; final suite result: 122 backend tests passed. DR1-first is deferred; this change does not establish successful fresh discovery.
