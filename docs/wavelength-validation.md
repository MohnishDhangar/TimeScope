# Wavelength-prioritized observation selection

November 15, 2026. This is an exploratory comparison heuristic, not validated spectral matching or authorization for subtraction.

## Discovery and candidate budget

Preserved genuine SIA inventories contain obs_id, obs_collection, t_min/t_max, em_min/em_max, em_res_power, access_url and s_region. Detector 2 samples all reported the same exposure-wide range 1.1033–1.6499 µm; detector 5 samples reported 3.8113–4.43 µm. These broad bounds are not the wavelength at the submitted sky position and are not used as local wavelength matches.

The API accepts `selection_mode: temporal | wavelength_matched` and `detector: null | 1..6`. Temporal mode preserves evenly spaced distinct times in a detector, with DR1 preference for repeated acquisitions. Auto chooses the detector with the most distinct discovery times, with deterministic tie-breaking. Detector constraints are applied before selection. Wavelength mode retrieves up to `min(12, max(6, 2*requested_frames))` time-distributed candidate cutouts in that detector; it does not download the whole inventory. Its result is limited by that candidate sample, retrieval success, storage capacity and processing budget.

## Measured spectral inputs and limitations

The actual spatial WCS maps the requested ICRS center into each input image. The alternate WCS-WAVE then supplies approximate center wavelength and bandwidth in microns. Inspected source headers identify CNAME1W=Wavelength, CNAME2W=Bandwidth, both CUNIT=um, and label the product an approximation.

IRSA explicitly says this lookup is intended for visualization and recommends full CWAVE/CBAND calibration products for scientific analysis. TimeScope has not retrieved those full calibration arrays. The ranking is therefore labeled wavelength-prioritized, not science-validated matching. Fractional separation is absolute delta wavelength divided by mean wavelength. Approximate bandwidth separation is delta wavelength divided by mean local WCS bandwidth; missing bandwidth stays unknown. It is not a measured resolving power, full filter response overlap or uncertainty estimate. No remembered resolving-power constant is hard-coded.

## Deterministic ranking

Eligible pairs have distinct UTC acquisition times, positive measured wavelengths, matching detector/release and unit labels, matching pipeline versions when known, and at least 10% common valid output coverage where measured. The coverage floor is an engineering availability guard, not a scientific-quality threshold.

Within the candidate pool, retain pairs spanning at least 25% of the longest eligible baseline (a disclosed engineering preference against nearly adjacent epochs). Minimize fractional wavelength separation; break ties by longer elapsed time, higher coverage and observation IDs. Preserve the best pair, then fill additional requested frames with the nearest center-wavelength neighbors in that metadata context. Additional frames may remain spectrally different. Unknown wavelengths cannot be treated as matched, and absent/insufficient eligible pairs produce an actionable unavailable state.

All results remain quantitative_comparison_allowed=false. Units and release equality do not validate calibration; PSFs, backgrounds and response functions are not matched.

## Genuine before/after evaluation

Original FITS checksums were verified, arrays reprojected and common mask coverage recomputed. No new NASA traffic was used for this audit. Exact identities, metrics and hashes are in wavelength-validation.json. The candidate pools below are the preserved showcase observations, not a claim of exhaustive archive optimization.

| Field / pair | Days | Δλ (µm) | Fractional separation | Approx. local bandwidths | Common coverage |
|---|---:|---:|---:|---:|---:|
| Original temporal endpoints |373.18|0.074662|4.805%|1.963|80.05%|
| Original recommended |373.18|0.074662|4.805%|1.963|80.05%|
| Southern temporal endpoints |373.18|0.064792|4.707%|1.962|79.34%|
| Southern recommended |187.50|0.003267|0.232%|0.097|76.48%|
| M101 temporal endpoints |377.99|0.467155|11.529%|12.975|90.86%|
| M101 recommended |205.18|0.073443|1.686%|1.947|73.08%|

No better eligible pair was available within the original six-frame pool. The southern recommendation has a substantially smaller approximate wavelength separation at the cost of temporal baseline and coverage. M101's endpoint pair spans different releases, while its recommendation uses two DR1 observations. M101 still lacks sufficient bright-peak matches for an alignment summary. None establishes variability or motion.

## Reproduction

```sh
.venv/bin/python scripts/validate_wavelength.py /path/to/original /path/to/southern /path/to/m101 --output docs/wavelength-validation.json
.venv/bin/python -m pytest -q
npm --prefix frontend run build
```

`--annotate-bundles frontend/public/showcase` attaches verified bandwidth/version measurements and recommendations without changing preview images, original source identities or existing partial/scope warnings. Never annotate a different frame/hash.

## Sources

- https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/ — WCS-WAVE semantics and visualization fidelity; CWAVE/CBAND guidance.
- https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/ — wavelength/bandwidth lookup procedure.
- https://irsa.ipac.caltech.edu/Missions/spherex.html — official wavelength/resolving-power overview.
- https://arxiv.org/abs/2404.11017 — instrument overview; not used as a source of product-specific calibration.

All sources checked November 15, 2026. Recommendation UI preserves the time/wavelength chart and supports applying a suggested pair to synchronized comparison. Share links retain detector, selection mode and frame count. Whole-session cache identity includes those settings and processor version; discovery metadata cache identity excludes frame count/mode/detector because its unfiltered inventory request is unchanged.
