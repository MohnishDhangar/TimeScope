# Comparison diagnostics and offline showcase

## Scope

The bright-peak diagnostic is a preliminary geometric sanity check, not a fitted astrometric solution or an object classifier. It uses calibrated arrays reprojected from preserved original FITS files, never PNG brightness values.

## Method

1. Preserve SOURCE and FULLSAMPLE informational flag bits; mask other flagged and nonfinite pixels using the preview policy.
2. Reproject onto the session's common TAN grid.
3. Estimate background and scatter using Astropy sigma-clipped statistics; select local maxima above background plus five times that scatter with a 5-pixel maximum filter.
4. Reject candidates within two pixels of image borders and any whose 5×5 centroid patch contains missing data.
5. Compute background-subtracted positive-weight centroids. Match mutual nearest peaks within a fixed 2-output-pixel radius.
6. Report match count and common valid coverage. Report median radial separation only with at least three matches. This count threshold is an engineering guard, not a scientific confidence threshold.

Risks: field crowding, wavelength dependence, blended sources, PSF changes, moving sources and incorrect associations can bias centroids. The 2-pixel association radius truncates measurable offsets: a gross shift can lead to absent or incorrect matches. We have not confirmed reference stars against Gaia, fitted a transform or propagated positional uncertainty. No quantitative difference imaging is enabled.

## Real-data result

Session `23577cd786a24f24bedec59e7c5366ae`: six real SPHEREx detector-2 frames, with 15 frame pairs. Each pair had 10–18 mutually matched peaks; median separations ranged from about 0.11 to 0.31 output pixels. These results must not be described as catalog-validated astrometric precision. Center wavelengths differ substantially. Provenance, original hashes, parameters and per-pair measurements accompany the exported manifest.

## Reproduce

```bash
.venv/bin/python scripts/audit_session.py 23577cd786a24f24bedec59e7c5366ae
.venv/bin/python scripts/export_showcase.py 23577cd786a24f24bedec59e7c5366ae
npm --prefix frontend run build
.venv/bin/python -m pytest -q
cd frontend
npx playwright test --workers=1
```

The offline showcase bundles PNGs and manifests only, approximately 72 KB on this machine. Its original FITS URLs remain available for independent retrieval. When the API is unreachable, the app loads this explicit cached example, displays a backend-unavailable banner, and disables live search. It never silently substitutes this field for a failed coordinate query. This supports backend-independent static hosting, not offline installation or downloads of original archive files.

## Sources

- https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.maximum_filter.html
- https://docs.astropy.org/en/stable/stats/robust.html
- https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/
- https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/

## Comparison workspace

The time/wavelength chart plots acquisition UTC against wavelength at the field center. It is not a light curve or a spectrum. Click a point or focus it with Tab and press Enter/Space to select an observation. The current frame is mint; the reference has a gold outline.

Side-by-side mode includes an evidence panel derived from the selected pair's real metadata: observation identity, absolute elapsed time, center-wavelength separation, detector/release labels, science-unit labels, measured mask overlap and preliminary bright-peak geometry. Missing information is explicitly unavailable. Exact unit or wavelength equality is never treated as approval for subtraction. No arbitrary compatibility score or spectral tolerance is introduced.

The panel appears in the offline HTML evidence export too. Quantitative subtraction remains unavailable because response compatibility, PSF/background matching, independent registration and uncertainty propagation are unresolved. This completes the explanatory comparison workflow, not the scientific validation gate for subtraction.

“Blink selected pair” automatically alternates the current and chosen reference observations at the selected playback speed. Stopping it returns to the initial current observation. Single-observation blinking is disabled. Choosing a chart point, reference, view mode or timeline position stops playback. The ordinary Play button clears pair mode and plays the full sequence.

Validation: 17 frontend tests (16 browser tests plus one metadata-logic test) passed; production and hosted-mode builds passed. Tests cover missing wavelength data, UTC time calculation, same-observation handling, actual pair alternation, chart keyboard selection, exported evidence and mobile overflow. The full backend suite was unchanged by this milestone; its previous 33-test pass remains the last backend result.
