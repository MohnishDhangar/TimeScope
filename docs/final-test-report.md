# Urgent final acceptance tests

Current source candidate adds verified target presets and preserves two user-created successful sequences. Existing science/backend processing is unchanged. Backend: 122 passed, 0 failed/skipped, 4.19 s, one Starlette/httpx deprecation warning. Production build and lint passed. Frontend full Chromium/metadata result is appended after completion; earlier freeze checks were 28 passed. Added checks cover both new bundles with API blocked and preset coordinate filling/opening without archive requests. No behavioral tests removed.

Scientific recovery checked target coordinates against cited reference positions, two or more distinct acquisition times, WCS center against actual request, trusted NASA FITS source URLs, recorded SHA256 identities, actual preview accessibility and partial-result preservation. Raw FITS were not independently re-downloaded during recovery. Fields do not establish source detections.

Full frontend suite: 31 passed (30 Chromium scenarios and one metadata-logic check), 0 failures/skips, 18.6 s. Production build/lint passed.

Public initial pass on revision timescope-00007-hhw: 27 passed, four failed (three initial page.goto timeouts, one ERR_CONNECTION_CLOSED). Direct HTTPS root, health and bundle index returned 200; sampled Cloud Run logs show 200 for page/assets/images. Underlying cause not established; do not attribute it to archive discovery. Retrying only the four failed scenarios; result recorded below when observed.

## Spectral explorer verification

Recorded 2026-11-15T18:31:12.704219+00:00. On the scientific-development worktree based on 81a72755925f14fc037e29a042e85e9d49e00fea: backend `python -m pytest -q`: **122 passed**, one existing Starlette/httpx deprecation warning. Frontend `npx playwright test --workers=1`: **34 passed in 22.2s** (includes three spectral tests); production build and oxlint passed. Real provider smoke test retrieved three HTTP 200 tiles at indices 26/62/99, retained the same field, disclosed missing channel 51, passed mobile horizontal-overflow and return-to-temporal checks, with no captured page errors. See spectral-validation.json. This is local verification; public verification is recorded separately after deployment.

Public spectral smoke on revision `timescope-00008-s5w` passed the same three genuine cube channels, missing-layer handling, mobile layout and return to temporal images. Separate public smoke passed all seven bundles, graph selection, playback/pause, comparison, HTML evidence with embedded PNGs, restored share mode and mobile overflow, with no captured page errors. These are smoke checks, distinct from the 34-check local regression suite. No new live SIA search was submitted.
