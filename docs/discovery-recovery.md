# Discovery outage recovery

November 15, 2026. IRSA capabilities, direct GET/POST SIA and TAP routes intermittently returned HTTP 502. An equivalent reordered SIA GET with `Cache-Control: no-cache` returned 289 actual records at 12:28:44 UTC for RA 133.79512917°,Dec −7.24514722°,FOV 5′. Subsequent identical requests failed again. The response alone does not prove cache behavior caused the difference.

## Recovery policy

- Direct SIA uses the successful parameter form with a maximum of two attempts and a two-second backoff. Same region, both DR1/QR3 collections and 1,000-record ceiling. Request ordering does not alter the scientific query.
- Successful discovery metadata are cached by exact coordinates, field width, collections, geometry version and record ceiling. Frame count affects later selection, not the discovery query; complete-session reuse still includes frame count and processor version.
- On discovery failure, only a matching inventory no more than 24 hours old may be used. The original retrieval UTC and inventory hash accompany the output. This does not establish a fresh discovery query.
- The captured original-field response is intentionally included as a small backend metadata snapshot. It contains observation IDs, times and trusted archive URLs, with the source response checksum. No raw FITS or synthetic preview is bundled for this recovery mechanism. Other coordinates/FOVs cannot use it; they require their own matching inventory or working archive discovery.
- Cutouts are requested for the actual submitted field and processed through the normal masks/WCS pipeline. Exact-request FITS cache hits are tracked separately per frame. Neither inventory reuse nor cached FITS is reported as a fresh download.
- The UI and evidence report disclose inventory reuse; public errors remain for fields without valid metadata. Cache expiry, new observations, coverage and record limits still apply. The snapshot does not provide permanent arbitrary sky coverage.

## Verification

52 Python tests passed, including query isolation, inventory expiry, partial-inventory rejection, bounded discovery retries and processing after a synthetic metadata outage. A genuine local run fetched four new original-field cutouts through the recovery path, aligned all four, and verified their FITS SHA-256 hashes. No frames were skipped. See discovery-recovery-local.json. This is real cutout retrieval with cached metadata, not successful fresh discovery or proof of variability.

Public recovery acceptance is recorded separately after deployment. The original endpoint failure remains an upstream dependency; this is a bounded, disclosed resilience mechanism.

Sources: https://irsa.ipac.caltech.edu/ibe/sia.html and https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/ (retrieved November 15).


## Public acceptance completed

Revision `timescope-00002-8kk`, source `d7516b97baa8df8df0020b6149558b76a1e71386`, build `040249c9-5fbd-4702-8c80-b0bdf99da300` succeeded. The public browser form requested the original field with four frames. It downloaded four genuine FITS cutouts (all `cutout_cached: false`), aligned and displayed them in 16.634 seconds. Metadata came from the exact-query inventory retrieved at 12:28:44 UTC; fresh discovery remains unreliable and is not claimed. Correct coordinates and image dimensions, side-by-side comparison and offline evidence export passed. The export retained the metadata warning and per-frame download status.

Background progress advanced from “Retrying discovery through direct SIA” to “Downloading and aligning 4/4 · 3 usable · 0 skipped” during 12 seconds with no polling. A simultaneous second search returned HTTP 429; the examples endpoint returned HTTP 200. A repeated identical completed query reused its retained session and was labeled as reuse. Raw evidence and image/source identities are in discovery-recovery-cloud.json; exact deployment identity is in discovery-recovery-deployment.json. The screenshot in docs/img/public-live-recovery.png shows the working real session.

All 52 Python tests and 19 frontend checks passed before deployment, together with lint and production build. No additional Cloud Run resource was provisioned. Other coordinates need their own matching inventory or successful live discovery. This recovery is intentionally limited rather than presenting arbitrary cached observations as a different field.
