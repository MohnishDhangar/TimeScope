# Public Cloud Run verification — 2026-11-15

Fresh unauthenticated public API and Chromium checks against the existing revision. No deployment or infrastructure changes.

| Field (RA, Dec; FOV) | Terminal result | Observed elapsed | Attempts |
|---|---|---|---|
| 103.4893, -24.5365; 1.2 arcmin | archive_timeout | 60.944 s | 4 |
| 133.79512917, -2.24514722; 5 arcmin | archive_timeout | 62.098 s | 5 |

Both were fresh jobs, not retained-session reuse. Both failed during discovery; neither used historical inventories or retrieved FITS. Returned observation counts are unknown, not zero.

All three bundled fields passed playback, stepping, side-by-side comparison, zoom control, mobile width and embedded-image evidence export checks. No browser JavaScript errors. Retry payload preservation used clearly synthetic interception to avoid another archive job. Real timeout UI was separately verified. Concurrent scientific submissions returned HTTP 429; bundled examples remained usable. Missing sessions and private job artifacts returned 404.

The exact DR1-only query and AWS retrieval remain unverified from Cloud Run. These require a tested application route; this deployed revision uses combined collections. The community field search also uses an enclosing circle for a square FOV rather than the exact curl circle.

Fresh arbitrary-coordinate discovery remains unverified because the official archive returned errors during validation. No underlying outage cause was established.

Detailed results, original server failure classifications, polling timestamps and configuration: [cloud-runtime-verification.json](cloud-runtime-verification.json). Tests ran against `timescope-00003-t87`; full software tests and container build were not repeated because application code was unchanged.
