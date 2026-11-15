# Approved observatory integration

Integrates approved redesign merge `761b199e489e4f8b8bff8d1a8122771eb4f880a7` with the discovery repair and previously preserved wavelength-selection work. The original worktrees remain intact.

Preserved: graphite/red design, three workspaces, fixed viewer, independently scrolling analysis, library auto-navigation, playback/blinking, synchronized comparison/pan/zoom, metadata/chart selection, native/smooth display, share restoration, evidence export, exact-query historical inventory disclosures, bounded archive retries, private-artifact restrictions, storage/session bounds, detector selection and approximate wavelength recommendations. No dependencies or cloud resources changed. Discovery remains the existing combined DR1+QR3 query; DR1-first and AWS adapters are not implemented.

Baseline reproduced: 106 Python tests, 20 frontend checks, build and lint passed. Integrated validation: **121 Python tests; 26 frontend checks (25 Chromium scenarios and one metadata-logic check); production build and lint passed**. One dependency deprecation warning remains. Tests retain prior behavioral assertions with updated navigation and the approved Search observations label. Synthetic failures are intercepted and make no NASA requests.

All three genuine bundles passed browser coverage. Four added browser scenarios assert stationary viewer bounds during analysis scrolling, useful image dimensions and no clipping/overflow. Additional manual browser inspection measured eight viewport sizes in single/compare modes; a 360×640 regression (60-pixel image) was fixed to approximately 144 pixels without changing the palette/layout structure. Screenshots under `docs/img/observatory-*` show actual application output.

Original FITS checksums and all three wavelength-validation results were reproduced exactly offline. The southern field recommendation remains 0.232% approximate center-wavelength separation versus 4.707% at temporal endpoints, with shorter baseline and lower common coverage. These are candidate-pool heuristics, not validated photometric/spectral compatibility.

Deployment/public verification are recorded in `frontend-integration-validation.json` and `cloud-deployment-record.json` after the committed source is published. No fresh target discovery or detection is inferred from bundled fields. Named-target audit remains incomplete; record archive-failed attempts separately from successful sequences.

## Deployed and publicly verified

Source `2ec672dabb10bd2a47dad442e1c9423196af4950`, revision `timescope-00004-q59`, build `e6c906a0-43ad-4374-9b03-87f1e4869724` **SUCCESS**. All 26 checks passed again against the public URL. Actual original-field search recovered through historical metadata and four fresh FITS in 64.35 s; automatic viewer navigation, comparison and evidence export passed. Full results/configuration are in the linked JSON records.
