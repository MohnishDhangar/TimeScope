# Submission copy — draft for the final reviewed competition version

Current implementation: the deployed discovery repair, source `a11ae4e35c0b44aa118e1ab8ebf2987108fa072b`. If more features are integrated, revise this text against the final tested source before submission. No official submission has occurred.

## Form verification and links

The official 2026 landing page states November 15, 11:59 PM local time as the project deadline: https://www.spaceappschallenge.org/2026/ . The challenge-page fetch timed out during this repair, and the authenticated submission form was not inspected. The fields below follow the project's reported/historical form structure; match them to the actual Local and Global forms. Do not assume the presentation/video limits or all required fields have been verified for your Local Event.

- Project: **TimeScope**.
- Challenge: **Planet X and SPHEREx**.
- Public app: https://timescope-331427520592.us-central1.run.app/ .
- Independent showcase: https://timescope-spherex.roanpaste16.chatgpt.site/ .
- Repository: https://github.com/MohnishDhangar/TimeScope . Repair branch still needs owner publication/verification; final `submission-v1` tag has not been created. Use the immutable final source link once it exists.
- Presentation: **Missing — prepare/upload the final seven-slide artifact and insert its public URL.**
- Demo video: **Missing — record/upload the final version with English captions and insert its public URL.**

The user reports that repository, app, PPT and video links are all needed. Prepare all four. Check each in an unauthenticated browser and retain submission confirmation.

## High-level summary

TimeScope makes repeated NASA SPHEREx observations accessible through a web-based temporal sky viewer. Enter celestial coordinates or open a genuine example, then step through dates, blink observations and compare aligned infrared images with synchronized zoom. Wavelength, coverage and original FITS provenance help users interpret differences carefully. Shareable views and downloadable evidence support investigation and teaching. The application distinguishes historical metadata, cached cutouts and new downloads, and reports archive failures honestly. It is an exploration tool motivated by the search for faint or moving objects, not a claimed Planet X detection.

## Detailed description

Finding meaningful change in astronomical images requires knowing when, where and at which wavelengths observations were made. Raw archive interfaces and FITS files create a substantial barrier for students and the public, while a visually striking difference alone can be misleading.

TimeScope connects a React/TypeScript viewer to a FastAPI scientific pipeline. The backend queries NASA/IPAC IRSA for SPHEREx DR1 and QR3 spectral images covering the requested region. It deduplicates observations by identity and detector, prefers DR1 duplicates, selects distinct acquisition times and retrieves bounded FITS cutouts. Astropy WCS and reproject place masked observations onto a common north-up/east-left TAN grid. A shared asinh stretch produces transparent PNG previews without claiming that display values are calibrated photometry.

Users can play the timeline, select dated filmstrip frames, blink endpoints or a pair, and compare synchronized panels. The time-versus-wavelength chart reveals an important confounder: images of the same field at different dates may also sample different wavelengths. Metadata expose acquisition dates, local center wavelengths, valid coverage, source URLs and checksums. Evidence cards embed selected previews and provenance for offline reading.

Public archive errors are handled with bounded retries and explicit failure classes. Runtime discovery metadata expire after 24 hours. A fixed bundled historical inventory can recover only its exact original query, with its real retrieval date and checksum retained. Later observations may be missing. Historical recovery is never described as fresh discovery, and another field is never substituted. Downloaded FITS and exact-request FITS-cache hits have independent flags. Three genuine bundled fields keep the viewer usable without live discovery.

## Validation and limitations

This repair reproduced 106 passing Python tests and 20 frontend checks, with lint, a production build and an actual successful Cloud Build. A fresh unauthenticated public browser checked all three bundled real-data fields, comparison, image loading, mobile layout and evidence export. The original-field public job used historical metadata and retrieved four fresh FITS cutouts, producing four usable frames; a changed declination failed with classified archive errors and displayed no substitute observations. The initial original-field browser polling attempt failed; reopening its existing completed session worked. Full evidence and this limitation are retained in `docs/discovery-repair-validation.json`.

Fresh arbitrary-coordinate discovery remains unverified because the official archive returned errors during validation. The cause was not established. Images differ in effective wavelength, PSF, calibration and usable coverage. The previews and preliminary bright-peak checks do not establish measured motion, variability, photometric compatibility or catalog-validated astrometry. This release has no difference imaging, catalog overlays or candidate detector. Wavelength-selection work is unfinished in a separate checkout and must not be claimed as deployed.

## NASA data

Actual SPHEREx DR1 and QR3 Spectral Images from NASA/IPAC IRSA, including 17 genuine bundled derived previews across three fields. The M101 sequence contains both releases; original and southern sequences use DR1. No all-sky cube is used.

- DR1 Spectral Images: https://doi.org/10.26131/IRSA678 .
- QR3 Spectral Images: https://doi.org/10.26131/IRSA662 .
- Official DR1 citation and prescribed acknowledgement: https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html .
- Official QR citation and prescribed acknowledgement: https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html .

Acknowledge NASA funding, the JPL/Caltech SPHEREx mission and NASA/IPAC IRSA. Use the prescribed publication acknowledgement from the official release page in final presentation credits; application source licensing does not relicense the observations.

## Space agency partner and other data

No additional space-agency or astronomical catalog dataset is integrated into this repair. Software dependencies and their licenses are listed in THIRD_PARTY.md. Do not list Gaia/SIMBAD as used datasets unless they are actually added and validated in the final release.

## Use of artificial intelligence — confirm final wording

AI tools assisted project planning, implementation, debugging, documentation and test design. Codex/ChatGPT assistance is verified by this development record; Claude assistance is reported in the project history and the owner should confirm the final tool list. Scientific claims are supported by recorded observations and validation, not AI-generated imagery or invented detections. The team is responsible for the submitted application and its claims. Do not claim that every generated output was independently reviewed unless that is verified.

The owner approved MIT for original TimeScope source and confirmed no earlier project code was reused. Do not expand that statement into an unsupported claim about every possible third-party asset.

## References

- Official challenge: https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/ . Challenge fetch timed out in this repair; do not describe it as successfully rechecked.
- NASA/IPAC SPHEREx mission: https://irsa.ipac.caltech.edu/Missions/spherex.html .
- Archive access: https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/ .
- Introductory notebooks: https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/ .
- Verified cutouts tutorial: https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/ .
- Actual processing, test, deployment and public-query evidence: README.md and docs/FINAL-STATUS.md in the final published source.
