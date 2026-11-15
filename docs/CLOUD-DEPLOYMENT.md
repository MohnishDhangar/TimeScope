# Urgent final deployment — authoritative current identity

Source `81a72755925f14fc037e29a042e85e9d49e00fea`, revision `timescope-00007-hhw`, 100% traffic. Build `7819ffc1-5624-4236-b381-f70ff6fbac6b` **SUCCESS**.

Image: `us-central1-docker.pkg.dev/timescope-spaceapps-2026/cloud-run-source-deploy/timescope@sha256:61bda9942a83183f39c392d41cbbfe74de6347dcd1375f9746131d867c896c22`. Ready UTC: 2026-11-15T18:01:34.596093Z.

Public URL: https://timescope-331427520592.us-central1.run.app/ . Seven genuine bundles / 33 frames. All five named reference fields have usable sequences, with Epsilon/RW partial status and source visibility caveats. Five coordinate presets and explicit bundle-open action are included. Barnard's preset uses 10′; the recovered 6′ unpropagated reference-position bundle may omit the contemporary source. No detection/motion/variability is established.

Resources/identity/environment/port/scaling/concurrency/timeouts were re-read and compared unchanged against the prior service. Previous revision timescope-00006-rzk is retained. Independent static showcase was not changed. Existing storage/admission limits and one scientific worker remain.

The earlier local submission-v1 tag is superseded and must not be overwritten or presented as this source. Submit the latest pinned commit. Final acceptance details follow; historical earlier records remain in Git and their JSON artifacts.

## Verified unchanged configuration

Gen2, 1 vCPU, 4 GiB, instance-based billing / CPU throttling disabled, service minimum 1 and maximum 1 instance, HTTP concurrency 10, request timeout 300 seconds, container port 8000 and one Uvicorn worker. These were re-read from Cloud Run after deployment. No hosting/resource/billing changes or duplicate budgets were made.

Cloud Run injects PORT; the entry point binds 0.0.0.0. Full frontend mode is explicitly built with `VITE_SHOWCASE_ONLY=false`. Source upload was inspected against the deployed commit: 182 files, all 23 genuine showcase PNGs, no virtual environment, node_modules, runtime cache, raw FITS or credentials. Local Docker is absent; the actual remote Docker build succeeded with existing pinned dependencies and Python 3.14, without changing versions.

Continuous CPU supports the background thread between HTTP polls. A maximum of one instance is not a distributed singleton guarantee: instance replacement can lose memory jobs/files. Do not deploy over an active scientific job. Predeployment log/session inspection found no observed active jobs. No forced restart was performed during this acceptance.

## Reproducible deployment

From the reviewed, committed repository root, using an authenticated gcloud identity and the already authorized trial project:

```sh
gcloud run deploy timescope --project timescope-spaceapps-2026 --source . \
  --region us-central1 --execution-environment gen2 --allow-unauthenticated \
  --port 8000 --cpu 1 --memory 4Gi --no-cpu-throttling --min 1 --max 1 \
  --concurrency 10 --timeout 300 \
  --build-service-account projects/timescope-spaceapps-2026/serviceAccounts/timescope-build@timescope-spaceapps-2026.iam.gserviceaccount.com \
  --service-account timescope-runtime@timescope-spaceapps-2026.iam.gserviceaccount.com \
  --update-env-vars TIMESCOPE_DATA_DIR=/app/data,TIMESCOPE_MAX_CACHE_MB=512,TIMESCOPE_SESSION_TTL_SECONDS=21600,TIMESCOPE_MAX_JOBS_PER_HOUR=12
```

The dedicated builder has `roles/run.builder`; no Owner/Editor workaround or long-lived service-account key was created. Retain the runtime identity and existing environment. The required APIs already exist; do not create unrelated infrastructure. Future resource/billing changes require an authorized revised budget. Do not manually set the reserved PORT environment variable.

If a blocking release defect requires rollback after jobs finish:

```sh
gcloud run services update-traffic timescope --project timescope-spaceapps-2026 \
  --region us-central1 --to-revisions timescope-00006-rzk=100
```

The rollback revision retains the same backend/interface but has the earlier 17-frame library. Retain its image for emergency rollback; do not delete submitted images during judging.

## Discovery, storage and admission policies

Astroquery and direct SIA share one orchestrator: at most six total wire attempts, redirects/transport retries disabled, no hidden capabilities lookup. Retryable failures are 429, 502/503/504, connect/read timeouts, resets and verified DNS/connect failures. Backoff has jitter, respects Retry-After and checks the remaining budget before requests and sleeps. Deterministic query/schema/parse errors are not retried. Valid empty results are reported as no matches and never masked with historical rows.

`TIMESCOPE_DISCOVERY_BUDGET_S` defaults to 90 seconds and is capped at 90. Public requests additionally cap discovery at 60 seconds to reduce the one-job lock-out. The cooperative 240-second total budget reserves 150 seconds for processing; promptly started public jobs normally retain approximately 180 seconds after maximum allotted discovery. These are allocations, not completion guarantees or strict thread cancellation. See [performance.md](performance.md).

Transient discovery failure tries the valid runtime exact-query inventory (24-hour TTL), then a bundled historical exact-query inventory (no age expiry), then an explicit error. Both validate the query identity, schema, timestamps and trusted URLs and reject future timestamps. Bundled content is never refreshed or re-dated. The only bundled inventory matches RA 133.79512917°, Dec −7.24514722°, 5′. Its original retrieval date, kind and checksum are exposed. Later observations may be absent. It cannot support Dec −2.24514722° or another field/FOV. Fresh/cached FITS are tracked independently.

`TIMESCOPE_MAX_CACHE_MB=512` limits aggregate runtime files, including downloads, duplicate session FITS, metadata, previews, partials and shared caches. Oldest inactive items may be evicted; inactive live sessions default to six hours. Active job/read leases, conservative reservations, atomic JSON writes and a 64 MiB download cap protect resources. Filesystem storage is memory-backed and ephemeral. The provisional cap is not a measurement of cloud directory usage or peak memory. Bundled products are image assets outside disposable runtime storage.

One scientific job runs; an occupied slot returns actionable 429 without an unbounded queue. HTTP readers remain supported, and a global 12-new-jobs/hour admission policy applies. Completed exact-query reuse includes all search settings and processor version and is labeled as retained reuse. In-memory inactive job records are bounded. Only intended PNGs and manifests are public under `/artifacts`; internal jobs, inventories, raw FITS and arrays are blocked. Health does not query IRSA and is not proof of retrieval.

## Latest integrated public acceptance

Revision `timescope-00004-q59` passed all **26 frontend checks** against the public URL (25 Chromium scenarios and one metadata logic check). These cover all three genuine bundles, graph selection, metadata synchronization, playback/pair blinking, synchronized pan/zoom, offline evidence, view restoration, failure/Retry behavior and desktop/mobile fixed-viewer geometry. Failure fixtures were synthetic interceptions, not fresh NASA queries. Backend source validation passed **121 tests**, production build and lint. Current build succeeded with unchanged dependencies/resources.

One genuine public form submission requested RA 133.79512917°, Dec −7.24514722°, width 5′, four frames, Auto detector, temporal selection. Session `8caa38ba3b5e4341af5fbeb90d77a014` completed; readiness was observed after **64.35 seconds**. Three live discovery requests timed out; the exact bundled-historical 289-row inventory retrieved 2026-11-15T12:28:44.186124+00:00 was disclosed. Four fresh FITS cutouts, zero FITS-cache hits and four usable frames. The browser navigated automatically to the viewer with no alert; comparison and evidence download passed. This was historical metadata recovery, not fresh discovery. Full manifest and events are in `frontend-integration-validation.json`.

Earlier integration source upload: 130 tracked files including the original 17 showcase PNGs. Pre/post configuration comparison verified CPU/memory/billing/scaling/concurrency/timeouts/port/environment/runtime identity unchanged. No independent-static-showcase deployment or modification occurred. Named-target validation remains incomplete; see `target-testing-status.md`.

## Earlier discovery-repair acceptance (historical)

Fresh unauthenticated Chromium verified all three bundled real fields, timeline/playback, synchronized comparison, image loading, evidence export and narrow-screen layout. Missing-session and private-artifact 404s passed. Independent static-fallback checks are recorded in the central validation file.

Exactly two fresh public search submissions were made:

| Test field | Query | Actual result |
|---|---|---|
| A | RA 133.79512917°, Dec −7.24514722°, 5′, 4 frames | Five live discovery attempts returned 502. Reused bundled historical metadata (289 saved rows, original November 15 12:28:44 UTC); downloaded four fresh FITS, no FITS-cache hits, four usable frames. API readiness observed at 47.385 s. |
| B (distinct from the bundled southern field) | RA 133.79512917°, Dec −2.24514722°, 5′, 6 frames | Five discovery attempts: four HTTP 502s and one timeout. No matching inventory was used; failed at discovery, with no observations displayed. Terminal result observed at 50.911 s. Row count is unknown, not zero matching observations. |

The first Field A browser attempt lost automatic polling and displayed the unavailable-session error although independent API polling observed completion. Its cause was not captured. Reopening the **same** retained session, without another search, passed snapshot disclosure, comparison, mobile layout and standalone evidence export. This reliability limitation is retained in the evidence, not hidden as a clean first-pass success. Public Retry was verified with a synthetic intercepted Busy response so it made no third archive request; the changed declination was preserved.

At the earlier repair gate, fresh arbitrary-coordinate discovery was unverified because archive requests failed; that historical limitation is superseded by the later six-frame public PASS described above. No cause for the archive 502s was established. Local probes and Cloud Run observations are labeled separately. Existing historical background/Busy verification is in `discovery-recovery-cloud.json`; the repair's controlled worker tests passed, but a new public concurrent scientific submission was not attempted beyond the two-query allowance.

## Billing reminder and judging availability

The user's earlier screenshot showed ₹28,569 free-trial credit remaining and ₹0 prior usage; it predates deployments. The user confirmed a 90-day trial beginning November 15, projecting expiry around **February 13, 2027**. Exact expiry, current credit and actual usage still require confirmation in Billing. No paid upgrade is authorized or performed.

Published rates retrieved November 15: us-central1 instance-based CPU $0.000018/vCPU-second, memory $0.000002/GiB-second. Continuously allocated 1 CPU + 4 GiB is approximately **$67.39 per 30 days**, **$202.18 per 90 days gross**, about two-thirds of $300 before free allowances and build/registry/logging/egress costs. Instance-based monthly free allowances include 240,000 vCPU-seconds and 450,000 GiB-seconds; billing-account-wide usage and current terms apply. Do not rely on them for the budget.

The existing project-filtered ₹25,000 gross-usage budget excludes credits, covers November 15–February 14 and has 20/40/60/80/100% notification thresholds. **Budget alerts are notifications, not spending caps.** No duplicate was created; actual email delivery is untested. The owner must monitor usage/credit and retain the submitted image/service through judging. No automatic asynchronous monitoring is promised. Keep one warm competition instance and the independent fallback; do not deploy post-deadline scientific features to the submitted URL.

Official documentation checked November 15: [deploy CLI](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy), [Cloud Run pricing](https://cloud.google.com/run/pricing), [Free Trial](https://docs.cloud.google.com/free/docs/free-cloud-features), [billing mode](https://docs.cloud.google.com/run/docs/configuring/billing-settings), [container contract](https://docs.cloud.google.com/run/docs/container-contract).

## Spectral milestone deployment

Source `6998261984131a20f0c060423f600f9db7361888`, build `0bc0a453-6b3d-40e3-92eb-8fde8adee67d` SUCCESS, serving revision `timescope-00008-s5w`, image `us-central1-docker.pkg.dev/timescope-spaceapps-2026/cloud-run-source-deploy/timescope@sha256:c2ec03f739c308687c6c95dc57495f94a0ca031a680000009d065f0c59d385f7`, Ready at `2026-11-15T18:35:51.192977Z`. Traffic is 100% on this revision. Before/after configuration comparison verified resources, environment, port, HTTP concurrency, timeout, runtime account, service scaling and instance billing unchanged. Prior revision `timescope-00007-hhw` is retained for rollback. Seven bundled fields (33 frames), playback, chart selection, comparison, embedded evidence, shared-view restoration and mobile overflow checks passed in fresh unauthenticated Chromium. The actual public cube renderer returned three HTTP 200 tiles at 1.378, 3.293 and 4.915 µm. No fresh archive-discovery query was made by this deployment smoke test. Evidence: spectral-public-validation.json and spectral-public-smoke.json. No independent showcase changes or recordings.
