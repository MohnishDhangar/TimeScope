# TimeScope master task — current handoff

This is an incremental Stage A report, not a final submission or completed scientific release. Deadline: November 15, 2026, 23:59 IST; feature cutoff 20:30 IST.

## Current recovery update

The active revision is now `timescope-00002-8kk`, source d7516b97baa8df8df0020b6149558b76a1e71386. A genuine public form search of the original field with four frames successfully downloaded and processed four new FITS files in 16.634 seconds. It used explicitly disclosed exact-query metadata reuse during the discovery outage; it is not a successful fresh discovery query. Background processing, Busy response, reader availability, comparison and evidence export passed on that live job. 52 Python tests and 19 frontend checks passed. Full records are in discovery-recovery.md and discovery-recovery-deployment.json. Historical StageA details below describe the first revision and its failed live attempts. Wavelength-selection and residual-imaging stages remain pending.

## Repository and release

Branch: main. Entry baseline: 91edb2014e4ae0203fc220aff2034fc574b1fc1d, clean. Implementation commits: d8472e6 (bounded ephemeral storage and public artifacts), e304f03 (Cloud Run source deployment configuration). Exact deployed source and image are in `cloud-deployment-record.json`. Documentation/evidence added after that fixed source are a separate documentation-only commit. Competition tag/release: not created; freeze is a later stage.

Changed implementation: backend/app.py, pipeline.py, new storage.py, frontend session recovery/frame-count control/disclosures, tests, resource measurement script, Docker and upload excludes. No raw FITS, runtime caches, environments or credentials staged. Existing scientific originals were preserved outside disposable runtime storage before testing cleanup.

## Public deployment

Primary: https://timescope-331427520592.us-central1.run.app

Independent fallback: https://timescope-spherex.roanpaste16.chatgpt.site

Service timescope, us-central1, gen2; revision timescope-00001-v78 serving 100% traffic; 1 CPU/4 GiB; instance-based billing; service min1/max1; HTTP concurrency10; timeout300; port8000/one worker. Startup CPU boost remains enabled. Actual Cloud Build succeeded with the pinned dependencies; no dependency or Python change. Image digest and source SHA recorded separately. Dedicated builder has roles/run.builder; runtime has no added project role. No Owner/Editor role was granted.

## Acceptance status

- Verified: public unauthenticated HTTPS; all three genuine bundles; comparison, zoom, share restoration, evidence download, mobile overflow; internal artifact denial.
- Genuine public coordinate form and API job creation: verified. Actual IRSA discovery/FITS retrieval: failed with HTTP502 at discovery in both attempts; no fresh frames or successful live search claimed.
- Background completion and Busy/readers: tested with a controlled local synthetic worker, not a successful cloud scientific workload.
- Expiry/recovery, leases and eviction: covered by local tests. Actual cloud revision replacement after a successful job: not performed.
- Static fallback remains independently hosted and unchanged.

## Science features

Existing qualitative temporal explorer, pair blinking and comparison evidence retained. Wavelength-aware selection/detector filter: not implemented. Exploratory calibrated-array residuals: not implemented. Catalog overlay/Source Inspector/candidate detection: not attempted this stage. No discovery or quantitative validation claimed. Quality-mask policy unchanged; authoritative flag audit remains open. Previous real bundle measurements are in example-validation.md and example-audit.json.

## Tests and resources

Reproduced baseline:33Python,17frontend. Current:45Python tests,18frontend checks (17browser scenarios,1logic check),production build and lint passed. Separate cloud-browser smoke checks passed. Remote Docker build succeeded; no local Docker build. Existing FastAPI/httpx deprecation warning remains.

Five offline real-FITS replays:0.302–0.377s per six-frame job, process peakRSS236052KiB, runtime data grew to121285890bytes under128MiB test cap. These omit discovery/network/startup. Production aggregate default512MiB,6h TTL,one scientific job,12new admissions/hour,oldest-first inactive eviction and active writer/reader leases. Measured Cloud Run memory samples around failed discovery jobs:~110–112MiB; full processing peak unverified. Cold/warm successful live-query latency unavailable.

## Budget and judging

User console screenshot:₹28569 free-trial credit before deployment,₹0 previous charges. User confirms expiry90days fromNov15, projectedFeb13,2027. No paid upgrade performed. Gross compute planning estimate$67.39/30days,$202.18/90days before free allowance/ancillary costs. Actual current remaining balance not retrieved. Project-filtered gross budget₹25000 with₹5000 increments configured; alerts are not caps or tested email delivery. No second warm service, VM or durable scientific storage created.

## Submission assets and user actions

Repository: https://github.com/MohnishDhangar/TimeScope (new commits are local until pushed). Presentation, video, submission text, third-party credits, license decision and final competition tag remain unfinished. The public deployed build is the Stage A source, not a final submission.

Still required: confirm license and AI/pre-existing-code disclosure; prepare/record/upload fixed demo and deck; complete official submission and retain confirmation. No NASA submission has occurred. Current official challenge page was inaccessible (502), so exact current form requirements remain unverified.

## Next milestone

Proceed to Stage B wavelength-aware observation selection and real-data before/after evidence. Preserve current deployment as known-working frontend/API baseline while upstream IRSA is unreliable. Then Stage C only if before feature cutoff and validated on genuine arrays. Use CLOUD-DEPLOYMENT.md as the authoritative infrastructure guide.
