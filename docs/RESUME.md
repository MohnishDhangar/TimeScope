# Resume checkpoint

## Master-task Stage A checkpoint (November 15, ~16:55 IST)

Master task supersedes earlier hosting choices: Google Cloud Run primary, ephemeral live sessions, one CPU/4 GiB/gen2/instance-based/min1/max1/concurrency10/timeout300. Actual primary URL https://timescope-331427520592.us-central1.run.app . Independent static fallback remains unchanged.

Repository main was clean at 91edb20 on entry. New implementation commits d8472e6 (aggregate storage/API hardening) and e304f03 (Cloud Run source configuration). Cloud Build succeeded using committed source e304f03, dedicated builder with roles/run.builder and a separate runtime identity. Serving revision timescope-00001-v78. Full source/image mapping is in cloud-deployment-record.json. gcloud is installed under the user's local lib; signed-in identity and project access work. Project timescope-spaceapps-2026, trial screenshot ₹28,569 remaining before deployment, user confirms expiry90days fromtoday (~Feb13). No billing upgrade. Project gross budget ₹25k, alerts at₹5k steps configured; delivery not tested.

Current checks reproduced:45Python tests,18frontend checks (17browser +1logic),build and lint passed. Storage defaults512MiB aggregate,6h TTL,leases,atomicmetadata,12newjobs/hour,oneactivejob,publicPNG/manifest allowlist. Internal artifacts not exposed. New frame-count form/link recovery and temporary-session disclosure. Existing raw local data preserved outside disposable runtime before cleanup testing. Five offline real-FITS jobs measured ~0.30–0.38s and peakRSS~231MiB; not network benchmarks.

Public all-three-bundle browser checks passed, including comparison/zoom/sharing/export/mobile. Both real public search attempts failed with IRSA502. Health correctly distinguishes archive failure. NO successful public live retrieval, cloud Busy gate on an actual successfuljob, or controlled cloud restart established. Cloud memory sampled~110–112MiB near failedjobs; not full-processing peak. No secrets in committed records.

NEXT: StageB wavelength-aware selection and detector constraint, using preserved realFITS to validate offline while archive is unreliable; then StageC exploratory residuals if before20:30IST. Do not duplicate hardening or provisioning. Do not mark cloudlive acceptance complete. No submission tag yet; later freeze at22:30 with fullchecks. Official challenge page still returned502 during this review. See authoritative docs/CLOUD-DEPLOYMENT.md and docs/FINAL-STATUS.md. Historical paragraphs above are superseded by this checkpoint.
