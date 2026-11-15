# AWS SPHEREx availability investigation — November 15, 2026

This is an availability investigation after the feature cutoff, not a new released feature. The working Cloud Run application, resources, strict archive allowlist and bundled showcase are unchanged. No new SIA/TAP or public TimeScope searches were made. The owner retains manual commit control.

## Sources and actual discussion

The supplied [NASA Space Apps discussion](https://github.com/nasa/spaceapps/discussions/2183) contains an AWS cloud-access suggestion in a participant reply. Organizers acknowledge access reports and an SME suggests other IRSA interfaces. Some November 14 replies reported SIA working then; they do not establish current availability. The thread alone does not establish a total archive outage or its cause. The user's separate report of a global-team announcement has not been independently sourced here.

[Official IRSA cloud documentation](https://irsa.ipac.caltech.edu/cloud_access/) identifies the public bucket `nasa-irsa-spherex`, region `us-east-1`, with `dr1/`, `qr3/` and `qr2/` prefixes and anonymous access. [The official cloud tutorial](https://caltech-ipac.github.io/irsa-tutorials/cloud-access-intro/) demonstrates partial FITS reads and explains that locating files by sky position is a separate discovery operation. No AWS account or provisioning was needed for these tests.

## Verified local access

- Anonymous DR1 listing: HTTP 200.
- Known DR1 spectral-image object: HTTP 206 for bytes 0–2879, with a valid FITS header. Total object size: 65,790,720 bytes.
- A subsequent bounded range-read experiment accessed genuine `IMAGE` and `FLAGS` sections: **[50, 50] pixels**, science unit **MJy / sr**, acquisition **2025-05-05T16:48:02.459 UTC**, detector **3**.
- Target: RA 133.79512917°, Dec −7.24514722°. Its WCS input pixel was [381.2227482677013, 153.73574541440237]. The object identity was taken from the existing historical inventory, not a new discovery query.
- **14 HTTP range requests**, **917,504 bytes**, **6.408 seconds** locally. No full-file download. These are one local experiment's results, not Cloud Run benchmarks or a latency guarantee.
- 2500 finite image pixels; 2421 pass the existing conservative preview mask. Neither count establishes a detected source, photometric measurement or scientific mask-policy validity.

The real response and measurements are in [aws-availability-validation.json](aws-availability-validation.json). No synthetic images or alternate field were used. Full-file SHA-256 was not measured; ETag is not presented as one.

## Implications for TimeScope

AWS file access is a verified alternative to IRSA-hosted FITS retrieval. Keep Cloud Run; no AWS hosting account, VM or new always-on service is needed. An integration would need a narrowly allowlisted, byte/request/deadline-bounded range reader, crop-aware WCS/spectral handling, tests against preserved real data and explicit retrieval provenance. Replacing the hostname alone is insufficient: S3 serves the full FITS object and does not implement IRSA's cutout query parameters.

Arbitrary-coordinate discovery remains a separate blocker. The bucket is organized by release/planning period/product rather than directly by RA/Dec. Root and release listings did not expose a top-level spatial inventory; no exhaustive recursive scan was attempted. Our existing historical inventory can identify only its supported exact query. A verified independent spatial inventory, externally supplied observation list or functioning archive discovery route is still needed for broader fresh searches. We must not present AWS file retrieval as restored arbitrary-coordinate discovery.

No code, dependency, hosting or resource changes were made. The next availability milestone, if pursued, is validated AWS-backed section retrieval with explicit metadata provenance; this investigation does not claim it is already in the deployed app.
