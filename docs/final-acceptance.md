# Final competition acceptance and handoff

## Executive result

The public temporal viewer meets the implemented coordinate/image/playback workflow and has a genuine fresh discovery/retrieval PASS for one arbitrary-coordinate field. Named-target field validation: three usable sequences, two archive-timeout blocks. No target detection, measured motion or photometric variability is established. Competition assets are review-ready; official submission requires the owner.

## Repository and production

Release worktree: `timescope-final`, branch `release/final-integration`. Original `timescope` and repair worktrees retain their prior work. The latest source/revision/digest are recorded in `cloud-deployment-record.json` after each verified deployment. Current data-library update is published only after checks; no second warm service or resource/billing change is permitted. The independent static showcase is preserved.

## Five targets

| Target | Requested RA, Dec (degrees) | Usable frames | Visibility | Outcome |
|---|---|---|---|---|
| Barnard's Star | 269.45207696, 4.69336497 | 0 | Field only; source unverified | BLOCKED |
| Epsilon Indi B | 331.04570833, -56.78344444 | 0 | Field only; source unverified | BLOCKED |
| RW Aurigae | 76.95652603, 30.40143817 | 2 | Field only; source unverified | PASS |
| R Draconis | 248.16761083, 66.75497942 | 4 | Field only; source unverified | PASS |
| WISE 0855 | 133.79512917, -7.24514722 | 4 | Field only; source unverified | PASS |

RW Aurigae has two usable frames out of four attempted and retains partial-sequence disclosure. R Draconis has four usable frames. WISE reference field has six bundled frames and a separately documented four-frame historical recovery. Barnard/Epsilon had bounded attempts before and after the read-timeout repair; all evidence remains in the two target JSON reports. Target positions/epochs and proper-motion limitations are explicit.

## Scientific evidence

Five bundled sequences contain 23 frames. Detailed dates, wavelengths, coverage and original provenance are in `final-field-audit.json` and each manifest. Original 17 FITS hashes/identities/dates/detectors/units/FLAGS and all three reference grids were rechecked; wavelength and overlap results reproduced exactly. Six newly bundled target previews preserve server-computed FITS checksums, not independently downloaded local raw FITS. Preliminary bright-peak diagnostics are not independent astrometric accuracy. Source visibility is unverified for every named target.

Fresh public field RA 133.79512917°, Dec −2.24514722°, 5′, six requested frames: no retained session, no historical metadata, first-attempt live discovery returned 290 rows; six fresh FITS; readiness observed at 44.799 s. Correct field, actual previews, comparison and evidence export were verified in Chromium. Full data: `final-fresh-search.json`. Earlier timeout remains in `final-fresh-search-before-timeout-repair.json`. Success for one field does not guarantee universal archive availability.

## Engineering evidence

Clean npm ci, production build and lint passed. Final backend suite: 122 passed, no failures/skips, one dependency deprecation warning. Target-library suite: 28 checks (27 Chromium scenarios, one metadata-logic check). Final public recheck is recorded in the deployment handoff. Original first browser run failed because its local server was absent; subsequent running-server checks passed. No tests were removed. Screenshots show actual 1920×1080, 1366×768 and mobile layouts. Fixed viewer/scroll/axis readability/invalid form/navigation checks passed.

## Remaining limitations and cuts

DR1-first route and AWS adapter are not implemented. Current combined-collection discovery uses a 35-second read ceiling constrained by the shared discovery/job budgets. No change to query radius or MAXREC was made. No spectra, calibrated residuals, catalog overlays, source inspector, candidate detector, quantitative photometry or motion claim. No organizer waiver was established. Actual authenticated submission form and team-specific media limits were not inspected; seven slides/30 seconds are conservative drafts supported by some 2026 local-event pages, not verified team-wide requirements.

## Assets and owner actions

Presentation: `../submission/TimeScope-presentation.pptx` (seven slides; XML structure checked; owner must inspect the actual rendered deck). Project, technical, scientific, sources and limitations documents, manual demo storyboard and checklist are in `../submission/`. Owner records the demo; no automated video is part of this release. MIT approved and no previous code reused per owner. Confirm AI-use wording, public media links and actual billing credit/expiry.

1. Review/open the deck and descriptions; confirm local form/media rules and AI disclosure.
2. Record and upload the demo manually; upload deck and verify both public URLs.
3. Publish the prepared local annotated tag with an authenticated Git client if CLI credentials remain unavailable.
4. Review and complete the official submission before 23:59 IST; preserve the confirmation.

No official submission has been performed. Budget notifications are not spending caps. Keep the frozen application/image through judging; future features belong on a separate branch.

## Final deployment identity

Application source `92dbf60b58ed085bc119e202182a9598dcfde215`; serving revision `timescope-00006-rzk`; build `c22c1c59-22e4-411c-8f86-ac955251f079` SUCCESS. Image `us-central1-docker.pkg.dev/timescope-spaceapps-2026/cloud-run-source-deploy/timescope@sha256:598a9b1a4a591d12de405a8a887bc06555fc116bb15da124e0cde20694522429`. Public HTTPS: https://timescope-331427520592.us-central1.run.app . Full traffic and configuration were compared before/after; required settings unchanged. Independent fallback returned HTTP 200 and displayed a real preview at 2026-11-15T17:20:33.894Z. The previous ephemeral live-session link returned 404 after replacement, confirming the documented lifecycle. No source code changes are planned after this freeze.

Final production verification: 28 checks passed against timescope-00006-rzk (1.6 minutes), including both newly bundled target sequences with APIs blocked. Final backend: 122 passed; production build and lint passed. Source upload filename footprint matched 182 tracked source files and all 23 showcase PNGs. No credentials, raw FITS, node_modules or runtime caches were included. Current publication is frozen after the documentation commit; tag publication status is reported explicitly in the final handoff.
