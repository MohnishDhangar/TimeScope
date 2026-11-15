# Five named challenge targets

Field-level PASS means a genuine usable sequence, not detection of the named object. Public requests use the deployed combined DR1+QR3 SIA orchestrator; original reference positions are not epoch-propagated source detections.

| Target | Requested RA, Dec (deg) | FOV | Usable frames | Visibility | Status |
|---|---|---|---|---|---|
| Barnard's Star | 269.45210000, 4.69340000 | 6.0′ | 6 | A — reference field processed; epoch-propagated target visibility unverified | PASS |
| Epsilon Indi B | 331.04570833, -56.78344444 | 5.0′ | 4 | A — reference field processed; epoch-propagated target visibility unverified | PASS |
| RW Aurigae | 76.95652603, 30.40143817 | 5′ | 2 | A — field processed; target visibility unverified | PASS |
| R Draconis | 248.16761083, 66.75497942 | 5′ | 4 | A — field processed; target visibility unverified | PASS |
| WISE 0855 | 133.79512917, -7.24514722 | 5′ | 4 | A — field processed; target visibility unverified | PASS |

## References, attempts and limitations

### Barnard's Star
Coordinate reference: https://simbad.cds.unistra.fr/simbad/sim-id?Ident=BD%2B043561a. Epoch: J2000. Query: `{"ra": 269.4521, "dec": 4.6934, "fov": 6.0, "frames": 6, "detector": null, "selection_mode": "temporal"}`.
Attempt UTC: 2026-11-15T17:04:34.624335+00:00. Result: PASS.
Discovery method: astroquery-sia-v2; inventory kind: None; returned row count: 387; failure: none recorded. Attempts: `[]`.
6 usable frames, 2025-08-20T23:02:22.517 to 2026-09-22T15:04:20.982; detectors [5]; center wavelengths 3.889–4.393 µm. Original identities, checksums, coverage and pair diagnostics are preserved in the accompanying JSON.
No source identification, measured motion or variable-star photometry is established. Unknown proper-motion/reference-epoch details remain unknown; wide fields are used for reference-position tests. WISE uses the challenge-provided coordinates, whose position epoch was not specified.

### Epsilon Indi B
Coordinate reference: https://adsabs.harvard.edu/pdf/2008MNRAS.383..831P. Epoch: Position epoch not established from retrieved table; no propagation. Query: `{"ra": 331.04570833, "dec": -56.78344444, "fov": 5.0, "frames": 6, "detector": null, "selection_mode": "temporal"}`.
Attempt UTC: 2026-11-15T17:05:31.901471+00:00. Result: PASS.
Discovery method: astroquery-sia-v2; inventory kind: None; returned row count: 489; failure: none recorded. Attempts: `[{"attempt": 1, "route": "Astroquery SIA (explicit query endpoint)", "code": "archive_http_5xx", "http_status": 502, "exception_class": "HTTPError", "elapsed_seconds": 0.165}, {"attempt": 2, "route": "direct SIA", "code": "archive_http_5xx", "http_status": 502, "exception_class": "HTTPError", "elapsed_seconds": 0.166}]`.
4 usable frames, 2025-09-29T13:48:39.400 to 2026-09-28T08:04:44.318; detectors [3]; center wavelengths 1.892–2.213 µm. Original identities, checksums, coverage and pair diagnostics are preserved in the accompanying JSON.
No source identification, measured motion or variable-star photometry is established. Unknown proper-motion/reference-epoch details remain unknown; wide fields are used for reference-position tests. WISE uses the challenge-provided coordinates, whose position epoch was not specified.

### RW Aurigae
Coordinate reference: https://simbad.cds.unistra.fr/simbad/sim-id?Ident=RW+Aur. Epoch: J2000. Query: `{"ra": 76.95652603458332, "dec": 30.401438173888888, "fov": 5, "frames": 4, "detector": null, "selection_mode": "temporal"}`.
Attempt UTC: 2026-11-15T17:06:18.540035+00:00. Result: PASS.
Discovery method: astroquery-sia-v2; inventory kind: None; returned row count: 348; failure: none recorded. Attempts: `[]`.
2 usable frames, 2025-09-01T10:04:17.466 to 2026-09-09T21:42:13.876; detectors [1]; center wavelengths 0.974–1.068 µm. Original identities, checksums, coverage and pair diagnostics are preserved in the accompanying JSON.
No source identification, measured motion or variable-star photometry is established. Unknown proper-motion/reference-epoch details remain unknown; wide fields are used for reference-position tests. WISE uses the challenge-provided coordinates, whose position epoch was not specified.

### R Draconis
Coordinate reference: https://simbad.cds.unistra.fr/simbad/sim-id?Ident=%40376084&Name=V%2A+R+Dra&submit=submit. Epoch: J2000. Query: `{"ra": 248.16761083294998, "dec": 66.75497941722, "fov": 5, "frames": 4, "detector": null, "selection_mode": "temporal"}`.
Attempt UTC: 2026-11-15T17:06:53.534340+00:00. Result: PASS.
Discovery method: astroquery-sia-v2; inventory kind: None; returned row count: 583; failure: none recorded. Attempts: `[]`.
4 usable frames, 2025-05-16T22:56:23.637 to 2026-06-12T20:39:42.160; detectors [3]; center wavelengths 1.642–2.329 µm. Original identities, checksums, coverage and pair diagnostics are preserved in the accompanying JSON.
No source identification, measured motion or variable-star photometry is established. Unknown proper-motion/reference-epoch details remain unknown; wide fields are used for reference-position tests. WISE uses the challenge-provided coordinates, whose position epoch was not specified.

### WISE 0855
Coordinate reference: https://hackathlone.com/challenges/planet-x-and-spherex. Epoch: Not specified in challenge. Query: `{"ra": 133.79512917, "dec": -7.24514722, "fov": 5, "frames": 4, "detector": null, "selection_mode": "temporal"}`.
Attempt UTC: 2026-11-15T16:36:01.977Z. Result: PASS.
Discovery method: exact-query-cached-inventory; inventory kind: bundled-historical; returned row count: 289; failure: none recorded. Attempts: `[{"attempt": 1, "route": "Astroquery SIA (explicit query endpoint)", "code": "archive_timeout", "http_status": null, "exception_class": "ReadTimeout", "elapsed_seconds": 20.224}, {"attempt": 2, "route": "direct SIA", "code": "archive_timeout", "http_status": null, "exception_class": "ReadTimeout", "elapsed_seconds": 20.13}, {"attempt": 3, "route": "Astroquery SIA (explicit query endpoint)", "code": "archive_timeout", "http_status": null, "exception_class": "ReadTimeout", "elapsed_seconds": 10.323}]`.
4 usable frames, 2025-05-06T02:33:29.930 to 2026-05-14T06:53:35.614; detectors [2]; center wavelengths 1.316–1.591 µm. Original identities, checksums, coverage and pair diagnostics are preserved in the accompanying JSON.
No source identification, measured motion or variable-star photometry is established. Unknown proper-motion/reference-epoch details remain unknown; wide fields are used for reference-position tests. WISE uses the challenge-provided coordinates, whose position epoch was not specified.

Urgent acceptance: Barnard and Epsilon Indi B successes were recovered from user-created retained public sessions and independently checked for requested coordinates, genuine metadata, distinct epochs and preview accessibility. No new discovery success is inferred from copying them. Barnard’s 6′ reference-position bundle does not establish visibility at its contemporary high-proper-motion position; the preset uses 10′ and no target detection is claimed. Epsilon uses the brown-dwarf reference position rather than the primary. Previous blocked attempts remain in JSON provenance.
