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

Scientific checksum/wavelength reconstruction was reproduced during this acceptance run; the 17 preserved original FITS hashes, identity/date/detector/unit headers and FLAGS presence were checked again. Software success is not scientific detection validation.

Final target-library build and lint passed; 122 backend tests passed again. Two new genuine target-bundle browser scenarios exercise API-unavailable loading, stepping, comparison, explicit bundle provenance and evidence export. Final suite: 28 checks, 27 browser scenarios plus one metadata-logic check. Production recheck result is recorded after the data-library deployment.

Bundle-notice integration initially exposed three assertion/fixture mismatches: the partial-result status locator became ambiguous, and two synthetic historical-reuse fixtures still declared themselves bundled. The locator now selects the partial status, and live-reuse fixtures explicitly set cached_showcase=false. Behavioral assertions remain intact; the complete suite was rerun.

Final library candidate: production build/lint passed; backend 122 passed (2.14 s); frontend 28 passed (13.0 s), no failed/skipped checks. Bundle exports explicitly disclose no fresh discovery/retrieval. PNG bytes/scientific identities for all six new target products match their original public processing manifests; raw FITS were not independently re-downloaded locally.
