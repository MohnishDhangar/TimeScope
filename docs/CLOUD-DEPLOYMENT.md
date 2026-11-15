# Cloud Run deployment — authoritative competition guide

Updated 2026-11-15. This guide supersedes older hosting proposals. The independent fallback remains https://timescope-spherex.roanpaste16.chatgpt.site .

## Account and deployment status

Project `timescope-spaceapps-2026` was verified active through gcloud. Billing is enabled. The user's console screenshot showed ₹28,569 remaining free-trial credits and ₹0 accrued charges. The user confirmed expiry 90 days from November 15: projected February 13, 2027. This is user-confirmed relative timing, not an API-retrieved expiry timestamp. No paid upgrade is authorized or performed.

Cloud Build succeeded and revision `timescope-00001-v78` is serving 100% of traffic. Primary URL: https://timescope-331427520592.us-central1.run.app . The source commit and immutable image digest are in `cloud-deployment-record.json`. Docker/Podman are absent locally, but the actual remote Docker build succeeded without dependency or Python-version changes.

## Fixed configuration

One `timescope` service in `us-central1`, gen2, 1 vCPU, 4 GiB, instance-based billing (`--no-cpu-throttling`), service min=1/max=1, HTTP concurrency 10, request timeout 300 seconds, container port 8000 and one Uvicorn worker. No traffic split. PORT is injected by Cloud Run; the application binds 0.0.0.0. The Docker build explicitly uses full-application frontend mode.

CPU remains allocated between polling requests to support background scientific work. One maximum instance is not a distributed singleton guarantee; replacements may lose jobs. Do not deploy while a job runs. Live files and links are ephemeral. Bundled data survive instance replacement inside the image; the separate static fallback survives Cloud Run outages.

## Commands

After interactive `gcloud auth login`, verify the project and trial credit. From the repository root:

```sh
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project timescope-spaceapps-2026
gcloud meta list-files-for-upload
gcloud run deploy timescope --project timescope-spaceapps-2026 --source . \
  --region us-central1 --execution-environment gen2 --allow-unauthenticated \
  --port 8000 --cpu 1 --memory 4Gi --no-cpu-throttling --min 1 --max 1 \
  --concurrency 10 --timeout 300 \
  --build-service-account projects/timescope-spaceapps-2026/serviceAccounts/timescope-build@timescope-spaceapps-2026.iam.gserviceaccount.com \
  --service-account timescope-runtime@timescope-spaceapps-2026.iam.gserviceaccount.com \
  --update-env-vars TIMESCOPE_DATA_DIR=/app/data,TIMESCOPE_MAX_CACHE_MB=512,TIMESCOPE_SESSION_TTL_SECONDS=21600,TIMESCOPE_MAX_JOBS_PER_HOUR=12
```

Use explicit project flags. Do not manually set reserved PORT or overwrite unrelated environment variables. If IAM denies a step, resolve the exact missing permission instead of granting Owner/Editor. Never create service-account keys. Inspect the completed service's configuration, revision, image digest and traffic before claiming success. Build committed source only.

The upload list was checked: no runtime data, raw FITS cache, environment or node_modules paths; genuine `frontend/public/showcase` artifacts were present. `.gcloudignore` and `.dockerignore` both exclude private environment files and key-file patterns.

## Runtime storage and API policy

`TIMESCOPE_MAX_CACHE_MB` covers ALL runtime file bytes, not just the shared FITS cache. Default 512 MiB is provisional local engineering headroom, not a Cloud Run measurement. Six-hour default TTL and oldest-first pressure eviction apply to inactive session directories and shared cache files. Leases protect active processing and public file readers. Conservative byte reservations precede downloads/copies/metadata/previews. JSON writes are atomic. Inactive `.part` files disappear with their expired session; failed request downloads remove partial files immediately. Bundled artifacts are outside runtime storage.

A retained live session with exactly matching query settings and processor version can be reused; UI labels the reuse. Expired links preserve query coordinates, field width and frame count and permit explicit retry. At most one scientific job runs; an occupied worker returns 429, without an unbounded queue. A process-wide 12-new-jobs/hour limit bounds admission (exact retained-query reuse is exempt). Inactive memory job records are pruned at housekeeping, retaining at most 64 plus the current admission.

Only numeric PNG previews and public `manifest.json` are served under `/artifacts/{session}/{name}`. Raw FITS, job state, inventories, arrays and partial files are not public. IDs, names, traversal and symlink escapes are checked. Health never queries IRSA and explicitly separates configured live search from last processing status.

The 240-second processing deadline is cooperative: checks occur after discovery, between downloads, during response chunks and before output rendering. Bounded blocking calls/retries may overrun the deadline before the next check. It is not a strict thread cancellation guarantee. A 1,048,576-source-pixel ceiling bounds science-image expansion before array conversion. No storage service or persistence volume is added.

## Cost and availability estimates

Pricing retrieved 2026-11-15: instance-based us-central1 CPU $0.000018/vCPU-second and memory $0.000002/GiB-second. One continuously allocated CPU + 4 GiB: $67.39 per 30 days, $202.18 per 90 days gross compute, before free tier or ancillary costs. Gross credit margin against $300 is $97.82. This is a planning estimate, not measured spend or a guaranteed cap.

Instance-based monthly free allowances are 240,000 vCPU-seconds and 450,000 GiB-seconds, aggregated across the billing account. Do not rely on them for the credit budget. Monitor Cloud Build, Artifact Registry, logs and egress too. Configure budget notifications around $50/$100/$150/$200/$250 (or billing-currency equivalents); alerts are not spending caps. A project-filtered ₹25,000 gross-usage budget was created for November 15–February 14, excluding credits from spend calculation, with thresholds at 20/40/60/80/100% (₹5,000 steps). Default billing notification recipients were retained. Delivery of an actual threshold email is not tested. Do not change to two CPUs, scale to zero, upgrade billing or create another warm service without an authorized revised budget.

## Evidence and remaining gates

See `performance.md`, `runtime-measurements.json`, `local-live-check.json` and tests. Local memory is not Cloud Run memory. Verify public HTTPS, all bundles, genuine live retrieval, background work between polls, Busy behavior, expiry/restart behavior, container memory and source/revision identity on the actual service. Preserve the final image digest and competition source tag after freeze; do not tag an unfinished release.

Official references (retrieved 2026-11-15):
- https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy
- https://docs.cloud.google.com/free/docs/free-cloud-features
- https://cloud.google.com/run/pricing
- https://docs.cloud.google.com/run/docs/configuring/billing-settings
- https://docs.cloud.google.com/run/docs/container-contract


## Deployment evidence and unresolved acceptance

Cloud Build initially failed to read its staging source object. Created dedicated build/runtime identities and granted the builder only the documented `roles/run.builder`; the runtime has no added project role. No Owner/Editor grant was made. A short service-account/IAM propagation delay caused another pre-build rejection; the subsequent build succeeded. Cloud Run startup CPU boost is enabled by default; the steady configured CPU is one. Service-level min/max annotations are both 1; CPU throttling is false, gen2, 4 GiB, concurrency 10 and timeout 300 verified from the API.

A fresh unauthenticated Chromium browser verified all three real-data bundles, comparison, zoom, shared URL restoration, evidence export and mobile layout. A separate public form submission created a genuine search; both public live attempts failed at IRSA discovery with HTTP 502, confirmed in Cloud Run logs. No successful public FITS retrieval or cold/warm live-search benchmark is claimed. Controlled local tests establish Busy/readers/background completion; those gates remain unverified on a successful cloud scientific job. No forced cloud restart was performed. Public 404 behavior for internal artifacts was verified.

`cloud-memory-observation.json` preserves Cloud Monitoring samples around the failed jobs (approximately 110–112 MiB). These are sampled distribution means, not a measured peak for a completed scientific workload. Actual paid usage/remaining credit after deployment has not yet been measured; the screenshot credit balance predates deployment. No automatic asynchronous monitoring is promised.

The competition tag has not been created; this is the initial release milestone, not the final competition freeze. Future scientific changes require their own tests and a verified deployment update.


## Current revision — discovery recovery

Revision `timescope-00002-8kk` now serves all traffic. Source `d7516b97baa8df8df0020b6149558b76a1e71386`. See discovery-recovery-deployment.json for the new image digest and actual build record. The resource/scaling configuration is retained.

Public form verification downloaded and processed four fresh original-field FITS cutouts in 16.634 seconds using a matching discovery inventory. Metadata reuse is explicit; fresh IRSA discovery was not successful. The same test verified background progress without polling, HTTP 429 on a simultaneous job, examples HTTP 200 and viewer/evidence export. This supersedes the prior unsuccessful-retrieval status for that supported field; arbitrary uncached-region live discovery remains subject to IRSA availability.

A successful original-field metadata snapshot, retrieved 2026-11-15T12:28:44UTC, is intentionally packaged for exact-region outage recovery with a 24-hour maximum age. Runtime metadata cache files are included in aggregate storage accounting. They contain no image arrays. Per-frame exact-request FITS-cache reuse is recorded separately. See discovery-recovery.md.
