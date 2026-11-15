# Cloud Run deployment — authoritative competition guide

Updated November 15, 2026, after the discovery repair. This replaces earlier conflicting hosting instructions. Deployment identity is machine-readable in [cloud-deployment-record.json](cloud-deployment-record.json); scientific and browser acceptance have one source of truth in [discovery-repair-validation.json](discovery-repair-validation.json).

## Current service and source

Public app: https://timescope-331427520592.us-central1.run.app/ . Independent static fallback: https://timescope-spherex.roanpaste16.chatgpt.site/ .

- Project/service/region: `timescope-spaceapps-2026` / `timescope` / `us-central1`.
- Ready serving revision: `timescope-00003-t87`, 100% traffic; no split.
- Deployed source: `a11ae4e35c0b44aa118e1ab8ebf2987108fa072b`, branch `release/discovery-repair`, clean at source upload.
- Actual Dockerfile build: `5c660eae-bc54-4a2a-a723-9ffe907a4afa`, **SUCCESS**.
- Immutable image: `us-central1-docker.pkg.dev/timescope-spaceapps-2026/cloud-run-source-deploy/timescope@sha256:e31cddca734514acb9280bcce981dfc4e01ac9b2626e9a67b13929a46f50dcfa`.
- One deployment in this repair. Previous revision `timescope-00002-8kk` retained for emergency rollback. The owner will manually commit the subsequent evidence-document edits; those edits do not change application code. No competition tag has been created.

## Verified unchanged configuration

Gen2, 1 vCPU, 4 GiB, instance-based billing / CPU throttling disabled, service minimum 1 and maximum 1 instance, HTTP concurrency 10, request timeout 300 seconds, container port 8000 and one Uvicorn worker. These were re-read from Cloud Run after deployment. No hosting/resource/billing changes or duplicate budgets were made.

Cloud Run injects PORT; the entry point binds 0.0.0.0. Full frontend mode is explicitly built with `VITE_SHOWCASE_ONLY=false`. Source upload was inspected against the deployed commit: 110 files, all 17 genuine showcase PNGs, no virtual environment, node_modules, runtime cache, raw FITS or credentials. Local Docker is absent; the actual remote Docker build succeeded with existing pinned dependencies and Python 3.14, without changing versions.

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
  --region us-central1 --to-revisions timescope-00002-8kk=100
```

The older revision lacks the new non-expiring historical-inventory policy, so rollback is an emergency measure, not the judging plan. Do not delete either image digest until the competition version is frozen and verified.

## Discovery, storage and admission policies

Astroquery and direct SIA share one orchestrator: at most six total wire attempts, redirects/transport retries disabled, no hidden capabilities lookup. Retryable failures are 429, 502/503/504, connect/read timeouts, resets and verified DNS/connect failures. Backoff has jitter, respects Retry-After and checks the remaining budget before requests and sleeps. Deterministic query/schema/parse errors are not retried. Valid empty results are reported as no matches and never masked with historical rows.

`TIMESCOPE_DISCOVERY_BUDGET_S` defaults to 90 seconds and is capped at 90. Public requests additionally cap discovery at 60 seconds to reduce the one-job lock-out. The cooperative 240-second total budget reserves 150 seconds for processing; promptly started public jobs normally retain approximately 180 seconds after maximum allotted discovery. These are allocations, not completion guarantees or strict thread cancellation. See [performance.md](performance.md).

Transient discovery failure tries the valid runtime exact-query inventory (24-hour TTL), then a bundled historical exact-query inventory (no age expiry), then an explicit error. Both validate the query identity, schema, timestamps and trusted URLs and reject future timestamps. Bundled content is never refreshed or re-dated. The only bundled inventory matches RA 133.79512917°, Dec −7.24514722°, 5′. Its original retrieval date, kind and checksum are exposed. Later observations may be absent. It cannot support Dec −2.24514722° or another field/FOV. Fresh/cached FITS are tracked independently.

`TIMESCOPE_MAX_CACHE_MB=512` limits aggregate runtime files, including downloads, duplicate session FITS, metadata, previews, partials and shared caches. Oldest inactive items may be evicted; inactive live sessions default to six hours. Active job/read leases, conservative reservations, atomic JSON writes and a 64 MiB download cap protect resources. Filesystem storage is memory-backed and ephemeral. The provisional cap is not a measurement of cloud directory usage or peak memory. Bundled products are image assets outside disposable runtime storage.

One scientific job runs; an occupied slot returns actionable 429 without an unbounded queue. HTTP readers remain supported, and a global 12-new-jobs/hour admission policy applies. Completed exact-query reuse includes all search settings and processor version and is labeled as retained reuse. In-memory inactive job records are bounded. Only intended PNGs and manifests are public under `/artifacts`; internal jobs, inventories, raw FITS and arrays are blocked. Health does not query IRSA and is not proof of retrieval.

## Public acceptance and limitation

Fresh unauthenticated Chromium verified all three bundled real fields, timeline/playback, synchronized comparison, image loading, evidence export and narrow-screen layout. Missing-session and private-artifact 404s passed. Independent static-fallback checks are recorded in the central validation file.

Exactly two fresh public search submissions were made:

| Test field | Query | Actual result |
|---|---|---|
| A | RA 133.79512917°, Dec −7.24514722°, 5′, 4 frames | Five live discovery attempts returned 502. Reused bundled historical metadata (289 saved rows, original November 15 12:28:44 UTC); downloaded four fresh FITS, no FITS-cache hits, four usable frames. API readiness observed at 47.385 s. |
| B (distinct from the bundled southern field) | RA 133.79512917°, Dec −2.24514722°, 5′, 6 frames | Five discovery attempts: four HTTP 502s and one timeout. No matching inventory was used; failed at discovery, with no observations displayed. Terminal result observed at 50.911 s. Row count is unknown, not zero matching observations. |

The first Field A browser attempt lost automatic polling and displayed the unavailable-session error although independent API polling observed completion. Its cause was not captured. Reopening the **same** retained session, without another search, passed snapshot disclosure, comparison, mobile layout and standalone evidence export. This reliability limitation is retained in the evidence, not hidden as a clean first-pass success. Public Retry was verified with a synthetic intercepted Busy response so it made no third archive request; the changed declination was preserved.

Fresh arbitrary-coordinate discovery remains unverified because the official archive returned errors during validation. No cause for the archive 502s was established. Local probes and Cloud Run observations are labeled separately. Existing historical background/Busy verification is in `discovery-recovery-cloud.json`; the repair's controlled worker tests passed, but a new public concurrent scientific submission was not attempted beyond the two-query allowance.

## Billing reminder and judging availability

The user's earlier screenshot showed ₹28,569 free-trial credit remaining and ₹0 prior usage; it predates deployments. The user confirmed a 90-day trial beginning November 15, projecting expiry around **February 13, 2027**. Exact expiry, current credit and actual usage still require confirmation in Billing. No paid upgrade is authorized or performed.

Published rates retrieved November 15: us-central1 instance-based CPU $0.000018/vCPU-second, memory $0.000002/GiB-second. Continuously allocated 1 CPU + 4 GiB is approximately **$67.39 per 30 days**, **$202.18 per 90 days gross**, about two-thirds of $300 before free allowances and build/registry/logging/egress costs. Instance-based monthly free allowances include 240,000 vCPU-seconds and 450,000 GiB-seconds; billing-account-wide usage and current terms apply. Do not rely on them for the budget.

The existing project-filtered ₹25,000 gross-usage budget excludes credits, covers November 15–February 14 and has 20/40/60/80/100% notification thresholds. **Budget alerts are notifications, not spending caps.** No duplicate was created; actual email delivery is untested. The owner must monitor usage/credit and retain the submitted image/service through judging. No automatic asynchronous monitoring is promised. Keep one warm competition instance and the independent fallback; do not deploy post-deadline scientific features to the submitted URL.

Official documentation checked November 15: [deploy CLI](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy), [Cloud Run pricing](https://cloud.google.com/run/pricing), [Free Trial](https://docs.cloud.google.com/free/docs/free-cloud-features), [billing mode](https://docs.cloud.google.com/run/docs/configuring/billing-settings), [container contract](https://docs.cloud.google.com/run/docs/container-contract).
