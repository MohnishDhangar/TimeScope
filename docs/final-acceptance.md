# Final competition acceptance

Started 2026-11-15 22:18 IST. Current worktree release/final-integration, HEAD 1f7f435; GitHub main matched at audit. Original timescope checkout has preserved uncommitted historical work; it is not the release source. Approved redesign is already integrated in 2ec672d. Production revision timescope-00004-q59, same source; full digest in cloud-deployment-record.json. No code redeployment is needed for documentation-only acceptance.

Implemented: public viewer, coordinates/FOV/count/detector controls, temporal/wavelength-prioritized selection, playback/blinking, synchronized comparison, graph and metadata, evidence export/sharing, exact-query historical recovery and resource controls. AWS adapter, DR1-first route, full response matching, spectra, residuals, catalogs and measured source motion are absent.

Final tests and five-target outcomes are recorded in their dedicated reports. Submission materials are in submission/. The owner records the demo. Official form limits and organizer waiver remain unverified. No official submission is claimed.

## Final outcomes

Five named targets were individually addressed: Barnard, Epsilon Indi B, RW Aurigae and R Draconis each received a fresh public job and were BLOCKED by archive timeouts. WISE 0855 reference-field PASS relies on the earlier verified public recovery (four fresh FITS; historical metadata) and the six-frame bundled sequence. No target identification is claimed. Coordinates, epochs, query settings and server failures are in challenge-target-validation.json.

Fresh uncached field RA 133.79512917°, Dec −2.24514722°, 5′, six frames: archive_timeout, observed terminal time 56.129 s. No historical inventory or unrelated images substituted.

Current rerun: 121 backend tests; 26 frontend checks locally and publicly; clean npm ci, production build and lint passed. Initial browser test run failed because the local server was absent; its successful rerun and exact commands are recorded. Source dependencies are unchanged.

Submission files include project/technical/scientific descriptions, attribution, limitations, manual demo storyboard, seven-slide PPTX and checklist. PPTX XML structure checked; owner must visually review it in PowerPoint and upload. Authenticated form and team-specific media constraints remain unverified. No organizer waiver or official submission claimed. MIT is already authorized; owner confirms no earlier code reuse.

Freeze/tag publication: Git CLI lacks push credentials and the connected GitHub tools do not expose annotated-tag creation. A local annotated submission-v1 tag can be prepared after committing; owner must push it using an authenticated Git client. Do not overwrite a prior tag.

Final transport repair raises the per-read ceiling from 20 to 35 seconds, bounded by remaining discovery time, to accommodate observed successful 24–25 s responses. Shared discovery/job budgets and retry caps remain unchanged. Synthetic transport regression added; final suite result: 122 backend tests passed. DR1-first is deferred; this change does not establish successful fresh discovery.
