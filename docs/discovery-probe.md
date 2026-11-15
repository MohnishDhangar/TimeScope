# IRSA discovery probe — November 15, 2026

This was one local requests-only pass, with two repeats per variant, no automatic retries and a one-second pause between requests. The user-supplied script was absent, so a minimal equivalent was created as `scripts/probe_irsa.py`. No probe was rerun. These are local measurements, not Cloud Run query results.

UTC interval: 2026-11-15T13:03:26.994514+00:00 to 2026-11-15T13:03:44.798139+00:00. Query: RA 133.79512917°, Dec −2.24514722°, FOV 5′ (circumscribed-circle SIA footprint).

| Variant | Attempts | Successful discovery responses | HTTP statuses | Durations (s) | Returned rows |
|---|---:|---:|---|---|---|
| sia-baseline | 2 | 0 | 502, 502 | 0.995, 0.308 | Not available (error responses) |
| sia-maxrec100 | 2 | 0 | 502, 502 | 0.257, 0.309 | Not available (error responses) |
| sia-dr1-only | 2 | 0 | 502, 502 | 0.322, 0.321 | Not available (error responses) |
| sia-qr3-only | 2 | 0 | 502, 502 | 0.435, 0.266 | Not available (error responses) |
| sia-no-cache-header | 2 | 0 | 502, 502 | 1.619, 0.382 | Not available (error responses) |
| tap-point | 2 | 0 | 502, 502 | 0.276, 0.302 | Not available (error responses) |

No variant returned a VOTable or a successful TAP table. All 12 requests returned HTTP 502. Their row counts are **unknown**, not zero matching observations. A homepage or capabilities HTTP 200, had one occurred, would not establish discovery success.

## Cloud Run evidence (separate from local probe)

The requested 200-entry, two-hour Cloud Run log read found the changed-declination job `d8c8b5b168094915bdd8fb7f2631267b`. At 12:44:16 UTC, SIA capabilities failed with `DALServiceError` / HTTP 502 and direct SIA failed with `requests.HTTPError` / HTTP 502 for the actual Dec −2.24514722 query. The captured body is an HTML Proxy Error page. Per-request durations were not logged and cannot be reported. **No underlying cause was established**; neither maintenance nor overload is inferred.

## Conditional route decision

All five SIA variants and TAP failed on both repeats. There is no measured advantage for lower MAXREC, split collections or a header change. Keep the existing scientific footprint and 1,000-record ceiling. TAP remains disabled: its real response and schema could not be validated. No spatial inventory fallback, presets or target audit is started in this repair.

Full per-attempt UTC times, URLs, HTTP statuses, durations, payload hashes, environment labels and release acceptance evidence have one source of truth: [discovery-repair-validation.json](discovery-repair-validation.json). Local diagnostic response files remain outside Git. The script can reproduce the diagnostic but should not be repeatedly run against a failing service.

Source for the TAP join, point containment and timing caveat: [official IRSA SPHEREx cutouts tutorial](https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/) (accessed November 15, 2026). Point containment alone does not establish full-field coverage. No untested TAP adapter was added.

## Repair deployment acceptance

Revision `timescope-00003-t87` was deployed once and checked publicly. The original query recovered with bundled historical metadata and four fresh FITS; the changed-declination query failed with four 502s and one timeout. Fresh arbitrary-coordinate discovery remains unverified because the official archive returned errors during validation. The first original-field browser polling attempt failed; reopening the same retained session passed. No further archive probes were issued. All exact results, IDs and elapsed times are in the central validation JSON.
