# Historical development checkpoints

The entries below are historical records. They include superseded deployment choices and test counts; consult FINAL-STATUS.md and CLOUD-DEPLOYMENT.md for current status.

# Resume checkpoint

## User intent
Continue building TimeScope for the SPHEREx challenge. User decided against switching to Lunar Landing Site Navigator. User asks for factual reports, real data, browser verification and continued work after usage limits reset. User-reported reset: 06:02 AM Asia/Kolkata; no automatic resumption has been scheduled.

## Workspace
Main code: <workspace>/timescope
Plans: ../TimeScope-Hackathon-Roadmap.md and ../TimeScope-Build-Plan.md
Hosted showcase checkout: <workspace>/timescope-showcase

## Completed
- Real SPHEREx retrieval, masks, WCS reprojection, qualitative playback and comparison.
- Bounded retries, partial results and exact-request cutout caching.
- Preliminary bright-peak alignment diagnostics (not catalog-validated).
- Stable observation/view links and offline HTML evidence cards.
- Cached-session selector; persisted job status with restart/retry handling.
- Public static showcase: https://timescope-spherex.roanpaste16.chatgpt.site
- Fresh unauthenticated Chromium verified HTTP 200, real images, comparison, share restoration and evidence download.
- Last suite: 24 Python tests, 12 Chromium browser tests, production build passed. Static-only bundle also tested separately with zero API requests.
- Configurable Python PORT and TIMESCOPE_DATA_DIR, non-root Dockerfile, healthcheck and compose.yaml prepared. Docker build NOT tested: no Docker/Podman installed.

## Current limits
Public showcase has cached data only; live coordinate search explicitly disabled. User has no Python hosting account/VM. Sites cannot host the Python/FITS backend. Do not claim full public live-search deployment.
No validated subtraction, catalog-confirmed registration, automated detections or discovery claims. Wavelength differences complicate temporal interpretations. No fresh IRSA success established by the recent test suite.

## Next work
1. Read current roadmap and deployment.md before selecting the next deliverable.
2. Full public backend still needs a suitable hosting path; do not assume user has an account or authorize paid services.
3. Scientific validation and additional verified demonstration fields remain outstanding and can progress without a hosting account.
4. Fresh-install bundled examples are now fixed and tested: 27 Python tests plus an empty-storage Chromium check. See deployment.md.
5. Follow docs/manual-acceptance.md for unverified live-service, real restart, cross-browser and accessibility checks.

## Hosting continuity
Reuse Site appgprj_6af8ca4ed2c881919c82c873e04650a2, public version 1. Source commit 9e36d3a93019dc56ee91ee9ce15a59058c6c6a97. Preserve .openai/hosting.json in hosted checkout. Synchronize main frontend changes deliberately. Never copy runtime data or credentials into static sources. Obtain new short-lived source credentials if needed; none stored here.

## Processes
Last observed local server PID 1083385: .venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000. Verify before using/stopping: PID may change. Temporary servers on 8010/8011 were stopped. Public showcase is remote and independent of local server.


## Latest major milestone: three-field gallery
Two additional actual downloaded/audited sequences are bundled: M101 (d943f95d272546aa8a2a01e656fc3c32, 5 frames, partial) and southern field (57b2c1c4360a4ca8a2486e8b6c97077f, 6 frames, saved-inventory subset). Read docs/example-validation.md and docs/example-audit.json. Direct SIA fallback bypasses flaky capabilities lookup and parses field names, not generic VOTable IDs. 33 Python tests and 15 Chromium browser tests passed. The southern field is NOT a complete sky search; M101 has insufficient bright-peak matches for an alignment summary. No discovery/variability claims.

Gallery public deployment is now version 3, source commit 338223e4502306d9ae093a8335cf9977ebfbc8f4. Public unauthenticated checks passed for both new fields, comparison, evidence exports, link restoration and mobile overflow. Additional-examples milestone achieved; do not redo retrieval. Next prioritize remaining scientific validation and submission materials / hosting gaps per roadmap and confirmed midnight November 15 IST deadline.

Latest public version is now 4: comparison workspace, commit 5e0d5c6562af7d39e5633285c11c6cf12892b387. Includes interactive time/wavelength chart, selected-pair blinking and pair evidence in UI + offline export. 17 frontend checks passed (16 browser scenarios, one pure logic test); public smoke verification passed. This is qualitative evidence interpretation, NOT completed scientific compatibility/registration validation. See docs/comparison-validation.md. Deadline remains midnight ending November 15 IST; prioritize submission readiness and any remaining release blockers.


