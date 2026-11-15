# Additional real-data examples milestone

Completed November 15, 2026 IST. Numeric details are in `example-audit.json`.

| Field | ICRS center (degrees) | Width | Usable epochs | Dates | Coverage |
|---|---|---|---|---|---|
| Original comparison field | 133.79512917, −7.24514722 | 5′ | 6 | 2025-05-06 – 2026-05-14 | 88–92% |
| M101 field | 210.80227, +54.34895 | 6′ | 5 | 2025-05-10 – 2026-05-23 | 76–97% |
| Southern comparison field | 134.4, −8.5 | 10′ | 6 | 2025-05-06 – 2026-05-14 | 86–92% |

## What was actually verified

Both new sequences were freshly downloaded as SPHEREx FITS cutouts. Original FITS SHA-256 hashes were checked during reconstruction, masks and WCS reprojection were retained, and diagnostics were recomputed from original arrays. Previews were inspected and browser tests exercised both fields with API requests blocked. All 33 Python and 15 Chromium tests passed at this checkpoint.

M101 contains diffuse infrared structure; all pair diagnostics had insufficient bright-peak matches. One of six requested cutouts returned HTTP 422 and was skipped; the UI and manifest disclose the partial sequence. Its center wavelengths span roughly 3.82–4.39 µm.

The southern field has 32–55 mutual bright-peak matches per pair with median separations about 0.10–0.18 output pixels. The matching radius is two pixels, and the matches are not catalog-confirmed stationary sources. Center wavelengths span roughly 1.21–1.44 µm. No motion, photometric variability or discovery is established.

## How archive failures were handled

1. SIA capabilities lookup intermittently returned HTTP 502 while a direct SIA query returned data.
2. Added a bounded direct-SIA fallback using the same circular footprint, DR1/QR3 collections and 1,000-record limit. Correctly reads VOTable field names rather than generic IDs; checks service error status, schema and response size. M101's successful run used this route.
3. Additional positions at 270°, +65°; 83.8°, −5.4°; and a Barnard's Star reference field did not yield new sequences during these attempts.
4. For the southern field, the original saved discovery table supplied actual exposure footprint polygons. Convex spherical containment selected 183 candidate records covering the new center, then fresh cutouts were requested at the new coordinates. The six usable observations are a subset, not a complete archive query. Manifest records the source inventory hash and scope. Original field images were not relabeled or reused as new-coordinate cutouts.

Sources:
- https://irsa.ipac.caltech.edu/ibe/sia.html — direct SIA parameters, footprint semantics, repeated collection constraints.
- https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/ — M101 coordinates and SPHEREx cutout workflow.

These checks establish usable real-data examples for qualitative exploration. Independent catalog registration, PSF/spectral matching, quantitative subtraction and hosted live search remain separate unfinished milestones.
