# Urgent final acceptance tests

Current source candidate adds verified target presets and preserves two user-created successful sequences. Existing science/backend processing is unchanged. Backend: 122 passed, 0 failed/skipped, 4.19 s, one Starlette/httpx deprecation warning. Production build and lint passed. Frontend full Chromium/metadata result is appended after completion; earlier freeze checks were 28 passed. Added checks cover both new bundles with API blocked and preset coordinate filling/opening without archive requests. No behavioral tests removed.

Scientific recovery checked target coordinates against cited reference positions, two or more distinct acquisition times, WCS center against actual request, trusted NASA FITS source URLs, recorded SHA256 identities, actual preview accessibility and partial-result preservation. Raw FITS were not independently re-downloaded during recovery. Fields do not establish source detections.

Full frontend suite: 31 passed (30 Chromium scenarios and one metadata-logic check), 0 failures/skips, 18.6 s. Production build/lint passed.
