# Discovery outage recovery

November 15, 2026. IRSA capabilities, direct GET/POST SIA and TAP routes intermittently returned HTTP 502. An equivalent reordered SIA GET with `Cache-Control: no-cache` returned 289 actual records at 12:28:44 UTC for RA 133.79512917°,Dec −7.24514722°,FOV 5′. Subsequent identical requests failed again. The response alone does not prove cache behavior caused the difference.

## Recovery policy

- Astroquery SIA and direct SIA share one orchestrator with at most six total wire attempts and jittered 2/4/8/16/30-second exponential backoff, limited by the remaining budget. Astroquery uses an explicit endpoint without capabilities lookup; transport retries and redirects are disabled. The direct route retains the previously successful parameter form. Same region, both DR1/QR3 collections and 1,000-record ceiling. Request ordering does not alter the scientific query.
- Successful discovery metadata are cached by exact coordinates, field width, collections, geometry version and record ceiling. Frame count affects later selection, not the discovery query; complete-session reuse still includes frame count and processor version.
- On discovery failure, a runtime exact-query cache entry may be used for up to 24 hours. The intentionally bundled historical exact-query inventory has no maximum age; future-dated or invalid inventories are rejected. The original retrieval UTC and inventory hash accompany the output. This does not establish a fresh discovery query.
- The captured original-field response is intentionally included as a small backend metadata snapshot. It contains observation IDs, times and trusted archive URLs, with the source response checksum. No raw FITS or synthetic preview is bundled for this recovery mechanism. Other coordinates/FOVs cannot use it; they require their own matching inventory or working archive discovery.
- Cutouts are requested for the actual submitted field and processed through the normal masks/WCS pipeline. Exact-request FITS cache hits are tracked separately per frame. Neither inventory reuse nor cached FITS is reported as a fresh download.
- The UI and evidence report disclose inventory reuse; public errors remain for fields without valid metadata. Runtime cache expiry, coverage and record limits still apply. Bundled historical metadata retain their original timestamp and hash; observations released later may be missing. The snapshot does not provide permanent arbitrary sky coverage.

## Verification

52 Python tests passed, including query isolation, inventory expiry, partial-inventory rejection, bounded discovery retries and processing after a synthetic metadata outage. A genuine local run fetched four new original-field cutouts through the recovery path, aligned all four, and verified their FITS SHA-256 hashes. No frames were skipped. See discovery-recovery-local.json. This is real cutout retrieval with cached metadata, not successful fresh discovery or proof of variability.

Public recovery acceptance is recorded separately after deployment. The original endpoint failure remains an upstream dependency; this is a bounded, disclosed resilience mechanism.

Sources: https://irsa.ipac.caltech.edu/ibe/sia.html and https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/ (retrieved November 15).


## Public acceptance completed

Revision `timescope-00002-8kk`, source `d7516b97baa8df8df0020b6149558b76a1e71386`, build `040249c9-5fbd-4702-8c80-b0bdf99da300` succeeded. The public browser form requested the original field with four frames. It downloaded four genuine FITS cutouts (all `cutout_cached: false`), aligned and displayed them in 16.634 seconds. Metadata came from the exact-query inventory retrieved at 12:28:44 UTC; fresh discovery remains unreliable and is not claimed. Correct coordinates and image dimensions, side-by-side comparison and offline evidence export passed. The export retained the metadata warning and per-frame download status.

Background progress advanced from “Retrying discovery through direct SIA” to “Downloading and aligning 4/4 · 3 usable · 0 skipped” during 12 seconds with no polling. A simultaneous second search returned HTTP 429; the examples endpoint returned HTTP 200. A repeated identical completed query reused its retained session and was labeled as reuse. Raw evidence and image/source identities are in discovery-recovery-cloud.json; exact deployment identity is in discovery-recovery-deployment.json. The screenshot in docs/img/public-live-recovery.png shows the working real session.

All 52 Python tests and 19 frontend checks passed before deployment, together with lint and production build. No additional Cloud Run resource was provisioned. Other coordinates need their own matching inventory or successful live discovery. This recovery is intentionally limited rather than presenting arbitrary cached observations as a different field.

## Historical inventory durability repair (November 15)

Runtime caches retain the 24-hour TTL. Bundled historical inventories remain available after 60 days, with strict query, schema, URL and timestamp validation. The file is never refreshed or re-dated. Manifests, viewer banners and standalone evidence identify `inventory_kind` and the actual original retrieval time. Per-frame `cutout_cached` remains independent: only a recorded false value is described as FITS retrieved for this request. Unknown legacy retrieval status stays unknown.

Baseline reproduced in the isolated repair worktree: 52 Python tests, 19 frontend checks, lint and production build passed. Focused repair tests: 29 Python tests passed (synthetic metadata, mocked clock and generated test FITS; no archive requests). Browser disclosure/export checks are recorded in the final repair validation report. The unfinished wavelength work in the original checkout is preserved and excluded from this repair.

## Bounded discovery repair

The default configurable `TIMESCOPE_DISCOVERY_BUDGET_S` is 90 seconds, capped at 90; the public API further caps discovery at 60 seconds because discovery occupies the one scientific slot. A 150-second processing reserve is enforced within the cooperative 240-second job budget. Public jobs starting promptly retain approximately 180 seconds after their maximum allotted discovery phase. These are engineering allocations, not guaranteed completion times. Historical genuine Cloud Run four-frame metadata-recovery processing took 16.634 seconds; five local preserved-FITS replays took 0.302–0.377 seconds without network. See `performance.md`; neither is a latency promise for a new field.

Only 429, 502/503/504, connect/read timeouts, connection resets and verified DNS/connect failures retry. Retry-After is honored if another attempt fits; otherwise discovery stops. Invalid queries, other 4xx, deterministic VOTable errors and schema failures stop without retry or historical substitution. A valid zero-row response reports no matching observations and never consults the cache. Fallback after transient failures tries the valid runtime exact-query cache, then bundled historical metadata, then returns the classified error. Real polling messages identify the current route, actual prior failure/backoff and subsequent retrieval phase. Server logs preserve each exception; the public receives a safe error code/message.

Focused verification reproduced 86 Python tests and three browser checks, including actual Astroquery client serialization with a one-request mock transport, both route budgets, mocked backoff/clock/jitter, Retry-After, schema/query failures, valid empty results, historical provenance and Retry with the changed declination. All HTTP/FITS failure fixtures are synthetic; these checks do not demonstrate fresh archive availability. The one-pass real probe and prior Cloud Run errors are recorded separately in `discovery-probe.md` and `discovery-repair-validation.json`.
