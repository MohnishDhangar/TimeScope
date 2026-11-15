# Data, software and disclosure

NASA SPHEREx spectral images are provided by NASA/IPAC IRSA. The original and southern showcases use DR1; M101 includes DR1 and QR3. Verified release DOIs: DR1 spectral images https://doi.org/10.26131/IRSA678 ; QR3 spectral images https://doi.org/10.26131/IRSA662 . Follow the releases' prescribed acknowledgment wording linked from IRSA.

Sources: https://irsa.ipac.caltech.edu/Missions/spherex.html ; https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/ ; https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/ . Each observation retains original source URL, acquisition identity, detector, wavelength and checksum where available. Target coordinate references are in docs/challenge-target-validation.json. Catalog values used for testing are not measured SPHEREx detections.

Scientific software: Astropy, Astroquery, NumPy, SciPy, reproject, Pillow, PyVO. Application: React, TypeScript, Vite, FastAPI, Uvicorn. See THIRD_PARTY.md and dependency license records. Source license: MIT, approved by the owner. NASA and third-party data are not relicensed by the source-code license.

AI tools assisted planning, coding, debugging, documentation and test design. The team is responsible for the submitted work. Owner confirmation of the final tool list/review wording remains needed. Owner confirmed no previous project code was reused.

Named-target validation used CDS SIMBAD reference positions for Barnard’s Star, RW Aurigae and R Draconis, and the published Epsilon Indi Ba position cited in the target register. These catalog/reference positions support field selection only; no catalog overlay or measured SPHEREx source identification was added.
