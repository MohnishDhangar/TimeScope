# TimeScope — discovery repair handoff, November 15, 2026

This is a verified availability milestone, **not the final competition freeze or official submission**. Deadline remains 23:59 IST tonight. Full measured evidence has one source of truth: [discovery-repair-validation.json](discovery-repair-validation.json).

## Deployment and repository

Public application: https://timescope-331427520592.us-central1.run.app/ . Independent fallback: https://timescope-spherex.roanpaste16.chatgpt.site/ .

Repair branch `release/discovery-repair` is in the sibling `timescope-discovery-repair` worktree. The original `timescope` worktree remains on `main` with its unfinished wavelength edits preserved. These edits were not included in this deployment.

Deployed source: **a11ae4e35c0b44aa118e1ab8ebf2987108fa072b**. Ready serving revision: **timescope-00003-t87**, 100% traffic. Actual Docker Cloud Build **5c660eae-bc54-4a2a-a723-9ffe907a4afa** succeeded. Image digest ends **e31cddca734514acb9280bcce981dfc4e01ac9b2626e9a67b13929a46f50dcfa**; the full registry identity and timestamp are in [the deployment record](cloud-deployment-record.json).

Configuration verified unchanged: us-central1, gen2, 1 CPU, 4 GiB, instance-based billing, min/max one instance, concurrency 10, timeout 300 seconds, port 8000, one worker. One deployment in this repair; no new platform, resource increase, budget or paid upgrade. Previous revision retained for rollback.

Commits created before the owner's instruction to commit manually:

- `84f86d3` — Preserve bundled historical discovery inventories with explicit provenance.
- `8f2c727` — Add bounded discovery retries and failure classification.
- `a11ae4e` — Prepare judging documentation and approved MIT license.

Final evidence/document changes after that source are intentionally **uncommitted for the owner**. Push from this shell failed because GitHub HTTPS credentials are unavailable. The owner will publish the branch through an authenticated terminal/client. No force-push, history rewrite, competition tag or GitHub release was created.

## Repair steps

| Step | Status and evidence |
|---|---|
| 1: historical inventories | Completed and verified. Runtime TTL stays 24 hours; bundled metadata survive a mocked 60 days without timestamp/hash changes. Exact query, schema, URL and future-date validation retained. Viewer, manifest and offline evidence identify inventory kind/date. |
| 2: bounded orchestrator | Completed and verified. Six total maximum attempts shared across Astroquery/direct SIA, no hidden capabilities calls or transport retries; jittered backoff/Retry-After within budget. Public discovery cap 60 s, processing reserve retained, classified safe errors, real progress events. Valid empty searches and invalid queries do not use snapshots. |
| 3: diagnostic probe | Completed once locally. Five SIA variants × two repeats plus TAP × two repeats: **12 HTTP 502 responses, zero successful discovery responses**. Returned row counts are unknown. Separate real Cloud Run logs also show archive errors. Cause unconfirmed. |
| 4: conditional new route | Skipped because every measured variant failed. No evidence supports a lighter/split request; no real TAP schema/response was available to validate an adapter. No spatial fallback, new presets or target audit attempted. |
| 5: release | Built/deployed once and publicly verified, with the initial browser polling limitation below explicitly retained. |

## Field-by-field public evidence

**A: RA 133.79512917°, Dec −7.24514722°, 5′, four requested frames.** Session `319f0923fe0d482da6317e579ec4b6ad`. Five discovery attempts returned 502. Used **bundled-historical** exact-query metadata retrieved **2026-11-15T12:28:44.186124+00:00** (289 saved rows). Four genuinely fresh FITS cutouts, zero recorded FITS-cache hits, four usable distinct acquisition times. API readiness first observed after **47.385 s**. This is historical-metadata recovery, not fresh discovery. Full observation IDs, SHA-256 values, dates, wavelengths and failed attempts are in the central evidence.

The first browser attempt lost automatic polling and showed the unavailable-session error while separate API polling observed successful completion. Its cause was not captured. Reopening the **same existing session** passed correct-field viewing, snapshot disclosure, comparison, mobile layout and evidence export, without another scientific job. This is a known reliability limitation, not a clean automatic-completion claim.

**B: RA 133.79512917°, Dec −2.24514722°, 5′, six requested frames.** Session `b4bb67e2736a4236ace7c1abd224fa99`. Five attempts: four 502s and one timeout; final `archive_http_5xx`. Terminal failure observed after **50.911 s**. No matching inventory was used, and discovery failed before retrieval/selection. No observations were displayed; archive row count is unknown. This field is distinct from the bundled southern example at RA 134.4°, Dec −8.5°.

Exactly two fresh public scientific submissions were made. Public Retry was checked by intercepting a **synthetic** Busy response, confirming the failed new declination was resubmitted; it sent no third archive request. All three genuine bundles passed timeline/playback, comparison, image and mobile checks. Evidence export, missing-session 404 and hidden internal artifacts passed. The independent fallback was checked separately; see central evidence.

**Fresh arbitrary-coordinate discovery remains unverified because the official archive returned errors during validation.** The archive's underlying cause is not established. No overload/maintenance explanation is claimed. Local probe latencies are not Cloud Run query latencies.

## Software and resource verification

- Reproduced baseline: **52 Python tests**, **19 frontend checks**, lint/build passed.
- Final release: **106 Python tests passed** (one dependency deprecation warning); **20 frontend checks passed** (19 browser scenarios and one metadata-logic check); lint and production build passed.
- Actual Dockerfile Cloud Build passed with the existing pinned environment. No Python/dependency version change. A clean-clone installation was not reproduced.
- Python 3.14.7, Node 26.10.0, npm 12.1.0 measured locally. The Docker Node 24 build succeeded.
- Storage/lease/expiration/admission and controlled background/Busy tests passed. No additional live concurrent scientific search was made beyond the two-query allowance; prior cloud background evidence remains historical and linked from the deployment guide.
- Aggregate runtime cap remains 512 MiB; TTL six hours. Actual cloud directory size, Python RSS, cold/warm successful fresh-query benchmarks and instantaneous peak container memory were not measured. Any Monitoring samples in the central report are sampled distribution means, not peaks. Existing local real-FITS replay measurements remain historical evidence in [performance.md](performance.md).

## Scientific scope and submission assets

Temporal viewer, genuine examples, exact-query recovery, comparison evidence and offline HTML export are implemented and verified as described. Wavelength selection is preserved as unfinished work in the original checkout and is not deployed. Difference imaging, catalog overlays, Source Inspector, target audit and candidate detection are not included in this repair. Quality-mask scientific limitations remain unchanged. No discovery, validated motion, variability or quantitative residual claim is made.

MIT was explicitly approved and added. The owner confirmed no earlier project code was reused. README/SETUP/third-party credits now describe the actual application. DR1 Spectral Images DOI 10.26131/IRSA678 and QR3 DOI 10.26131/IRSA662 were verified from official IRSA release pages; the M101 bundle actually contains both releases.

- [Standalone real Field A evidence](evidence/original-field-discovery-repair.html).
- [Actual repaired viewer screenshot](img/discovery-repair-original-field.png) and [honest Field B error](img/discovery-repair-field-b-error.png).
- [Submission draft](submission-text.md) and [30-second recording script](demo-script.md).
- Presentation artifact, recorded/uploaded video, exact submission tag and official submission confirmation: **not completed**.

## Owner actions and next checkpoint

1. Review and manually commit the final documents/evidence in `timescope-discovery-repair`; push `release/discovery-repair` using an authenticated Git client. Preserve the unfinished main-worktree changes separately.
2. Resolve whether to finish/integrate the already preserved wavelength milestone before the 20:30 feature cutoff. Do not deploy unfinished main as if it contains this repair.
3. Confirm final AI-tool disclosure, assemble/upload the seven-slide deck, record the exact final-version demo with captions and complete all actual Local/Global form requirements. Official challenge-page fetch timed out; exact current authenticated form fields were not inspected. User-reported repo/app/deck/video links remain required.
4. Freeze/tag the final competition source and image, verify public links, submit before 23:59 IST (aim 23:15) and retain confirmation. Do not alter the submitted scientific version during judging.
5. Confirm actual trial expiration (projected approximately 2027-02-13), remaining credit and usage in Billing. Current configuration estimates $67.39/30 days and $202.18/90 days gross, before ancillary costs and free allowances. Existing budget alerts notify; they are not spending caps. No automatic monitoring is scheduled.
