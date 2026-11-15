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




## Archived README checkpoints (before discovery repair)

These paragraphs describe historical builds, not the current release.

# TimeScope

Development milestone: real SPHEREx discovery, cutout retrieval, WCS reprojection and a qualitative temporal viewer. A public cached-data showcase is available; the live-search backend is not publicly deployed. This is not a validated motion-detection tool.

## Run locally

```bash
.venv/bin/python -m pip install -r requirements-resolved.txt
npm --prefix frontend install
npm --prefix frontend run build
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. The backend serves the compiled frontend and API from one origin. Prepare the example with `.venv/bin/python scripts/prepare_demo.py`, or use coordinate search in the browser. A cached example appears after successful preparation. Tests: `.venv/bin/python -m pytest -q`.

## Scientific limits

- The query uses DR1/QR3 wide survey collections and a 1,000-record cap, disclosed when reached. It is not a complete all-sky or deep-field search.
- Selects one detector with multiple times; detector identity does not guarantee wavelength compatibility.
- Deduplicates by observation ID plus detector, preferring DR1 when that key repeats. Observation ID alone is insufficient.
- Uses acquisition DATE-OBS, not product creation DATE.
- Retains SOURCE and FULLSAMPLE informational flags; other flagged pixels are excluded conservatively for previews. This policy needs further validation against scientific use cases.
- Common north-up/east-left TAN grid and shared asinh display scale. Transparent/checkerboard areas indicate invalid coverage. Display resampling adds no resolution.
- Center wavelength comes from the FITS alternate spectral WCS with spatial SIP removed. It does not characterize wavelength everywhere in the field.
- WCS round-trip tests passed; empirical registration against stationary sources, photometric compatibility and uncertainty propagation remain outstanding.
- No subtraction, motion measurement, source identification, discovery significance or automated detection claims.
- Cached sessions survive restart through manifests. In-flight jobs are marked interrupted on their next request after restart; retry to start a new job. One worker, one job at a time. Public authentication, quotas and operational hardening remain outstanding.
- The example uses the challenge-provided WISE 0855 coordinate converted to degrees; it does not establish a detection of that object.

## Sources and provenance

Implementation follows documentation, not copied public-project code:

- https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/
- https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/
- https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/
- https://irsa.ipac.caltech.edu/Missions/spherex.html

Real FITS cutouts, archive discovery tables and JSON provenance manifests are under ignored `data/`. Manifests retain source URLs, acquisition times, releases, SHA-256 hashes, cutout parameters, output WCS and display settings. Add exact dataset acknowledgments/DOIs for the released demonstration before submission. Keep the raw files out of Git.

## Verified first milestone (November 14, 2026)

A live query returned 289 records. Six real detector-2 cutouts were prepared spanning 2025-05-06 through 2026-05-14, with roughly 88–92% valid output coverage. Center wavelengths differ (about 1.13–1.59 microns). These are suitable for exercising qualitative viewing, not proving motion or variability. Ten backend tests and a Chromium browser test passed; the browser test checks cached frame loading, endpoint blinking, playback controls and mobile overflow. The production frontend build passed. A Dockerfile is provided but has not been built or deployed. Public hosting remains outstanding.

## Comparison viewer update

Smooth display (default) and native output pixels can be selected without modifying the underlying data. Output dimensions and angular sampling are shown. An approximate angular scale bar follows fit zoom on the small TAN field. Side-by-side reference selection shares normalized pan and zoom; dates and center wavelengths are displayed for both observations. Both Chromium tests pass, including rendering modes, synchronized transforms, scale changes, playback and narrow-screen overflow. Scientific compatibility remains unverified; no subtraction is enabled.

## Preliminary alignment and backend-independent showcase

Side-by-side mode now reports matched bright-peak counts, median separation and common coverage when diagnostics exist. These checks do not validate stationary reference stars or quantitative comparisons. See [method and limitations](docs/comparison-validation.md).

The frontend includes a small real-data showcase with its source provenance. It still works when API requests fail, explicitly labels cached mode, and disables live search. Browser testing includes blocking every API request and reloading a saved session. Fourteen backend tests and three browser tests pass for this milestone. Public hosting remains outstanding.

## IRSA retrieval resilience

On November 14 the reported `133.79512917, -9` cutout returned HTTP 503 with `Server busy, retry later.` The same upstream failure occurred with explicit degree units and smaller cutouts. A subsequent live discovery query also timed out. This is not evidence of invalid user coordinates.

The downloader now normalizes archive failures, caches validated downloads by exact URL/parameters, removes partial files, skips failed observations and serves partial sequences when at least two frames remain. Three consecutive failures stop further downloads; a between-frame time budget limits prolonged batches. Each request has bounded retries and connect/read timeouts. These are not a strict total wall-clock deadline. Download/coverage failures are recorded in retrieval-report.json and successful manifests. Partial results are visibly labeled. Public errors are actionable; unexpected exception details remain in server logs. Retry never substitutes the example sky field.

Tests cover synthetic 503 failures, partial success, cache isolation, cleanup, sanitized API errors and stale frontend metadata. Upstream recovery itself cannot be guaranteed. No full-file or third-party mirror fallback has been validated.

## Shareable views and offline evidence

Open a cached example or a completed search, then use **Copy view link**. Links retain ICRS coordinates, field width, current/reference observations (release + observation ID + detector), comparison mode, rendering mode, playback speed, zoom and normalized pan. Playback always resumes paused. The browser address also follows the current view. Older session-only links still work.

These links depend on the original host retaining the session or a matching bundled showcase. They do not upload data, establish permanent archival storage or make a localhost server public. Missing sessions leave the coordinates in the search form and explain how to retry; opening a link never starts an expensive archive search automatically. Missing selected observations are disclosed rather than silently represented as the requested frames.

**Download evidence card** creates a standalone HTML report with embedded full-field PNG previews, selected observation dates, center wavelengths, coverage, original FITS links, available source SHA-256 hashes, preliminary pair diagnostics, partial-sequence warnings and scientific limitations. Read it offline or print it to PDF. The images are uncropped even when the interactive view is zoomed; the report records that transform separately. The complete processing manifest and original calibrated FITS remain separate linked artifacts. The card is not a discovery report or quantitative analysis.

The loaded field center is displayed separately from the editable search form so unsubmitted edits cannot be mistaken for the coordinates of the images or exported evidence.

## Release resilience update

Cached fields can now be selected by their actual coordinates and field width. The API omits incomplete manifests or sessions with missing previews, and lists complete sequences before partial sequences. This exposes existing cached sessions; it does not certify additional targets. Showcase exports retain previously exported examples instead of replacing the index.

Queued, running and terminal job states are written atomically to each session's `job.json`. In this single-process deployment, a queued/running record absent from memory is reported as interrupted when requested after a restart. The original query is restored in the UI and Retry starts a new job. Completed manifests take precedence over stale job records. This is restart detection, not automatic task resumption or a multi-worker queue. Use one Uvicorn worker; persistence requires retaining the data directory.

Validation for these milestones: production frontend build, 24 Python tests and 11 Chromium browser tests. Browser coverage includes shared-view restoration, offline embedded evidence, missing sessions, interrupted-job retry UI, cached-field selection and the existing playback/comparison/resilience checks. Public deployment and live archive recovery are not established by these tests.

## Pre-deployment test review

Latest local rerun: 24 Python tests, 12 headless Chromium browser tests, and the production build passed. Added an actual playback advancement/pause/wrap check and an explicit accessible name for the speed control. Cached images are real; archive failures and interrupted-session UI are simulated in browser tests. Restart recovery is tested from persisted state, not by force-killing a live process. No fresh live IRSA success, Firefox/Safari coverage, production load test or scientific catalog registration validation is claimed.

Use [the manual acceptance checklist](docs/manual-acceptance.md) for visual, live-service, cross-browser and operator-assisted restart checks before release.


## Public showcase deployment

https://timescope-spherex.roanpaste16.chatgpt.site

Published version 1 with public access using Sites. A fresh unauthenticated Chromium session returned HTTP 200 and successfully loaded real previews, side-by-side comparison, a shared view URL, and an evidence download. The hosted build intentionally disables live coordinate search and makes no API requests.

The local full app remains available separately. Its container now supports a host-provided port and persistent data path, uses a non-root user, and includes a health check. Docker/Podman are not installed here, so the container build is unverified. Direct Python entry-point startup and configurable storage were checked. See [deployment operation and limits](docs/deployment.md).


## Fresh-install example availability

A backend with empty runtime storage now offers the packaged real-data example through its API. Opening it, comparing frames and reloading a shared view leaves live-search controls enabled. Local cached sessions override matching bundle identities, and unrelated missing sessions never silently substitute the example.

Verification: 27 Python tests passed. A Chromium check against an actual backend with a new empty data directory verified image loading, comparison, reload and enabled search controls without making a live archive query. Reproduce with `PORT=8012 TIMESCOPE_DATA_DIR=/path/to/empty-dir .venv/bin/python -m backend`, then `cd frontend && node scripts/check-fresh-backend.mjs`. This does not validate IRSA availability.

## Faster field and epoch navigation

The viewer now includes a dated thumbnail filmstrip with center wavelengths and selected-frame highlighting. Selecting a thumbnail pauses playback. Coordinate presets populate the live-search form without relabeling already-loaded images. Presets are disabled in the hosted cached-only build.

New-field attempts on November 15 IST: RA 270°, Dec +65°, FOV 8′ failed at IRSA SIA capabilities with HTTP 502. M101 at RA 210.80227°, Dec +54.34895° was attempted through the official tutorial's TAP route and also returned HTTP 502. Neither is a verified example. M101 coordinates and TAP recipe source: https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/ . `scripts/prepare_m101.py` remains an experimental retrieval script; its successful end-to-end path has not been validated. `scripts/prepare_demo.py` now accepts --ra, --dec, --fov and --frames for bounded field audits.

Validation: frontend builds pass and all 13 Chromium tests pass, including field-preset provenance isolation and filmstrip selection at mobile width.


## Three-field showcase

The gallery now includes the original comparison field, M101 (five usable observations) and a distinct field centered at RA 134.4°, Dec −8.5° (six usable observations). These are freshly retrieved SPHEREx cutouts with audited hashes and reconstructed diagnostics. M101 is partial; the southern field uses a saved-inventory subset. Both limitations are visible. See [the validation report](docs/example-validation.md).

Archive discovery now has a direct SIA fallback, with identical query geometry and collections, bounded responses and explicit VOTable error checks. Chronological ordering keeps diagnostics tied to the correct frames. Latest verification: 33 Python tests and 15 Chromium tests passed.

## Comparison workspace — version 4

The public viewer now includes a keyboard-accessible acquisition-time versus center-wavelength chart, automatic blinking of the selected pair, and pair-specific evidence about elapsed time, wavelength difference, detector/release, units, common valid coverage and preliminary geometry. The same evidence is included in the standalone HTML export. Identical observations and missing metadata are handled explicitly; subtraction remains unavailable.

17 frontend checks passed (16 browser scenarios and one metadata-logic test). A fresh public browser additionally verified chart selection, actual pair alternation, the evidence panel and export, mobile overflow and absence of page errors. See [method and limitations](docs/comparison-validation.md).
