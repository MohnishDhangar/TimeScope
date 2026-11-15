# Challenge compliance

Basis: https://hackathlone.com/challenges/planet-x-and-spherex . Official NASA page returned 502 on this acceptance run. No waiver of the five-target objective was verified.

| Objective | Implementation | Verification evidence | Status | Remaining limitation |
|---|---|---|---|---|
| Public tool | Cloud Run HTTPS | cloud-deployment-record.json; public browser suite | PASS | Archive dependency remains |
| Genuine SPHEREx images | DR1/QR3 FITS-derived previews | manifests and reproduced checksums | PASS | PNGs are visualization products |
| RA/Dec inputs | Validated coordinate form | API and browser tests | PASS | Fresh discovery can fail |
| Requested sky region | Shared centered TAN grid; no substitute field | WCS tests, original-field public recovery | PARTIAL | Fresh arbitrary field search blocked |
| Multiple epochs | Dated chronological frames | Three manifests; 17 frames | PASS | Different wavelengths/confounders |
| Video-like playback | Timeline/play/pause/step/blink | Chromium tests | PASS | No source detection implied |
| Assist moving-object inspection | Synchronized visual comparisons | chart/blink/comparison browser tests | PASS for workflow | No measured motion validated |
| Five named targets | Individual coordinate register and public requests | challenge-target-validation.json | See per-target outcomes | Field PASS is not detection |

## Eight optional considerations

| Consideration | Status | Actual implementation / limitation |
|---|---|---|
| Future releases | Partial | Existing DR1/QR3 discovery; adapting a new schema/release still needs work |
| 102-band visualization / stacking / spectra | Partial | Approximate center-wavelength chart, detector constraint and pair ranking; no full-band explorer, stack or spectrum |
| Add/subtract images | Not implemented | No calibrated residuals |
| Field of view | Implemented and verified | 1–15′ square field; enclosing discovery circle |
| Other telescope overlays | Not implemented | Catalog references in audit are not overlays |
| Coordinate URLs | Implemented and verified | Query/settings and frame/view restoration |
| Metadata/contamination | Partial | Units, masks, coverage, source provenance; no per-pixel flag inspector |
| Astronomical software | Implemented and verified | Astropy, Astroquery, reproject and PyVO; no Aladin integration |
