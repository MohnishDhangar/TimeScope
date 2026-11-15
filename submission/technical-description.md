# Technical description

React/TypeScript/Vite and FastAPI serve a single-origin application on Google Cloud Run. The scientific path is coordinate query → bounded DR1/QR3 SIA discovery → duplicate handling and observation selection → bounded FITS cutouts → IMAGE/FLAGS quality masking → Astropy WCS and reproject shared north-up/east-left TAN grid → shared asinh visualization scale → PNG previews and provenance manifest.

Temporal coverage and optional detector constraints are available. Wavelength-prioritized selection ranks a bounded candidate pool using approximate field-center spectral WCS, time separation and common valid coverage. It does not match full spectral response or PSFs.

Discovery retries, exact-query inventory reuse, temporary storage eviction, one scientific worker, public artifact allowlisting and clear partial-result errors constrain resource use. Historical inventories retain their original checksum and retrieval date; FITS cache hits are reported separately. Runtime sessions are temporary; downloaded evidence embeds preview images.

Current source/image/revision and unchanged Cloud Run configuration are recorded in docs/cloud-deployment-record.json. Existing SIA routes query both collections; a DR1-first route and AWS adapter are not implemented.
