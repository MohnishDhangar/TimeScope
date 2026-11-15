# Third-party software and data

Original TimeScope code is covered by the repository MIT license, authorized by the project owner on November 15, 2026. This does not relicense NASA observations, dependencies, trademarks or their notices.

## Software

React, React DOM and Vite use MIT terms; TypeScript uses Apache-2.0. Their exact resolved versions and transitive dependencies are in `frontend/package-lock.json`. Retain the installed packages' LICENSE files when redistributing them.

The scientific/backend stack includes FastAPI (MIT), Uvicorn (BSD-3-Clause), Astropy (BSD-3-Clause), Astroquery (BSD), PyVO (BSD-3-Clause), reproject (BSD-3-Clause), NumPy/SciPy (BSD family with additional bundled-library notices), Pillow (MIT-CMU), Requests (Apache-2.0) and Pydantic (MIT). Their pinned versions are in `requirements-resolved.txt`. [Installed Python license metadata](docs/dependency-licenses.json) records all pinned distributions; this inventory is not a legal compatibility audit. Distribution LICENSE/NOTICE files govern their individual terms and bundled components.

The frontend began from the standard Vite React template. NASA/IPAC notebooks and documentation informed the archive/WCS workflow; the owner confirmed that no code from an earlier personal project was reused. No claim is made that the upstream scientific algorithms were invented by this project.

## SPHEREx observations

The current repository contains 33 bundled previews across seven fields, all genuine derived visualization products from DR1 and QR3 Spectral Images. M101 includes both collections; the original and southern sequences use DR1. Per-frame manifests preserve the actual archive collection, observation identity, source URL, acquisition time and SHA-256. The images are not synthetic, and are not quantitative calibrated-array downloads.

- [DR1 Spectral Images: DOI 10.26131/IRSA678](https://doi.org/10.26131/IRSA678), verified from the [official DR1 overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html).
- [QR3 Spectral Images: DOI 10.26131/IRSA662](https://doi.org/10.26131/IRSA662), verified from the [official QR overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html).
- [Mission and publication-acknowledgement requirements](https://irsa.ipac.caltech.edu/Missions/spherex.html).
- [Official archive access documentation](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/) and [cutouts tutorial](https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/).

TimeScope acknowledges NASA funding, the joint JPL/Caltech SPHEREx mission, NASA/IPAC IRSA's data service and the instrument, calibration and archive teams. The official release pages require their prescribed publication acknowledgement and the appropriate release DOI; use that source text for publications and presentation credits. The spectral explorer additionally uses official DR1 all-sky cube visualization tiles, credited below. No external Gaia/SIMBAD catalog data are used. References checked November 15, 2026.

NASA/SPHEREx names identify the data and challenge; no agency endorsement or discovery claim is implied. Any future catalog, imagery, code or asset integration needs its own provenance and applicable notices.

## Spectral mosaic renderer

Caltech/IPAC Firefly is loaded from the official IRSA viewer service. Its BSD-style license and copyright are preserved in [Firefly.txt](docs/licenses/Firefly.txt). SPHEREx DR1 all-sky cube metadata and visual tiles are supplied by NASA/IPAC IRSA, DOI [10.26131/IRSA679](https://doi.org/10.26131/IRSA679). Data are not covered by the application MIT license.
