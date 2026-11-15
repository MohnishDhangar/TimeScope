# SPHEREx spectral explorer

Implemented fixed-field visualization of the official SPHEREx DR1 all-sky HiPS cube using Caltech/IPAC Firefly. Open any genuine temporal sequence, then select **Spectral explorer**. The loaded session coordinates and field width are retained; unsubmitted coordinate edits are not used. Select one of 102 official, nonuniform wavelength channel centers (0.753–4.988 µm). Channels 51 and 52 (one-based) are blank and are displayed as unavailable, with no interpolation. Previous/next/reset controls and URL channel restoration are supported.

The product is a mosaic assembled across acquisition times. Switching channels is spectral exploration, not temporal playback. These PNG tiles do not provide calibrated numerical spectra, fluxes, errors or detections. The separate JSON export preserves the field, selected channel, official product metadata/checksum and limitations; its measurements list is explicitly empty. The temporal HTML evidence card remains unchanged.

## Method and validation

Metadata are preserved in `frontend/public/spectral/properties.txt` and normalized in `product.json`, with original retrieval time and SHA256. Actual provider metadata define wavelengths, equatorial coordinates, tile sampling (12.88 arcsec; not PSF resolution), channel gaps and MJD range. Renderer URL and product root are fixed to official IRSA endpoints. No general proxy, all-sky download or new dependency is introduced. Provider errors and a 60-second initialization deadline are isolated inside this mode; the temporal viewer remains usable. External loader availability and future API changes remain dependencies.

Integrated Chromium validation retrieved HTTP 200 tiles for zero-based indices 26, 62, 99 (channels 27, 63, 100), displaying 1.378, 3.293, 4.915 µm at the same 5-arcminute field. Missing-channel disclosure, mobile horizontal-overflow check and return to temporal images passed; no browser page errors were captured. Three channels, not every available layer, were independently smoke-tested. Machine-readable evidence: `spectral-validation.json`. Screenshot: `screenshots/final/spectral.png`.

Official references: [HiPS cube tutorial](https://caltech-ipac.github.io/irsa-tutorials/spherex-hipscube/), [product metadata](https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties), [DR1 overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html), [cube DOI](https://doi.org/10.26131/IRSA679), [Firefly API](https://github.com/Caltech-IPAC/firefly/blob/dev/docs/firefly-api-overview.md). Firefly license: `licenses/Firefly.txt`.

Calibrated spectrum extraction, cross-survey comparison, catalog overlays, source measurements, motion fitting and numerical residuals are not implemented by this milestone.
