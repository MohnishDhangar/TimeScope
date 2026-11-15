# TimeScope local acceptance checklist

Use http://127.0.0.1:8000 with the local server running. These are procedures, not claims that each manual check passed. Record browser/version, date, observed result, and a screenshot for failures. Do not deploy solely because automated test counts are green.

## Baseline and visual checks

Open this exact cached session to make results reproducible:
http://127.0.0.1:8000/?session=23577cd786a24f24bedec59e7c5366ae

Expected: six observations; RA 133.79512917°, Dec −7.24514722°, width 5 arcmin. This is an example sky field, not a confirmed identification of WISE 0855.

| Check | Actions | Expected result |
|---|---|---|
| Initial view | Load the session above. | Image appears; output is 49 × 49 pixels. Dates, wavelength, coverage and source ID are visible. No false discovery claim. |
| Native vs smooth | Toggle Rendering. | Native has sharp pixel edges; Smooth interpolates. Stars do not gain real detail. Missing coverage remains checkerboard. |
| Timeline | Move slider through all six positions. | Observation counter, date, image and metadata change together; dates progress chronologically. |
| Playback | Play at Slow, Normal and Fast. Pause and wait 3 seconds. | Sequence advances at different rates; Pause freezes it. No image jumps caused by transform resets. |
| Stepping | At first frame choose Previous; at last choose Next. | Wraps to last and first respectively. |
| Blink | Press Blink endpoints repeatedly. | Alternates between first and last observations. This is an explicit click toggle, not automatic two-frame animation. |
| Side-by-side | Select View → Side by side, then each reference frame. | Reference matches its selected date. Current and reference wavelength labels agree with metadata. Same-observation comparison is labeled. |
| Shared transforms | Zoom to 2× and 5×, drag either panel, change current frame, then Reset view. | Both panels share pan/zoom; changing time retains the transform; Reset centers both at 1×. Scale bar changes inversely with zoom. |
| Masks and diagnostics | Compare observations with differing coverage. | Missing data is distinguished from dark sky. Diagnostics say preliminary; no significance or discovery score is presented. |
| Loaded vs edited coordinates | Change Dec in the form to −9 without submitting. | Loaded field still says −7.24514722. Export and share use loaded-image coordinates. |
| Cached-field selector | Pick each available entry, then Open cached real observations. | Loaded coordinates/FOV match that entry. Partial sequences have a warning; selecting an option alone does not load it. |
| Source links | Open original FITS and processing manifest. | Manifest is readable JSON with source IDs/query. FITS may download or fail upstream; record which. FITS retrieval failure is not a viewer pass. |

## Sharing and export

1. Select current frame 3 and reference frame 5; choose side-by-side, native rendering, and zoom/pan.
2. Click Copy view link. Paste into a new tab on the same machine.
3. Confirm identical observations, rendering, comparison mode and transform, with playback paused.
4. If clipboard access is denied, manually select/copy the displayed link. It must still reopen correctly.
5. Download evidence card. Open the downloaded HTML file, then disable network and reload that file.
6. Confirm two images are still visible and dates, field coordinates, wavelength and source hashes match the selected observations. Export uses full-field images, not the zoomed crop; it documents this.
7. Use the browser's Print → Save as PDF. Inspect clipping, wrapping and whether both previews and limitations appear. Print layout is a manual acceptance check.
8. Try this missing-session link:
   http://127.0.0.1:8000/?session=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa&ra=42&dec=-30&fov=8
   Expect a useful error, preserved coordinates and no automatic archive search or substituted example.

A localhost URL cannot be opened by a remote judge. Sharing across machines is a deployment check.

## Search, errors and resilience

| Check | Procedure | Expected result / interpretation |
|---|---|---|
| Browser validation | Submit a blank coordinate, RA 360, Dec 91, FOV 0 and FOV 16 in turn. | Browser prevents submission. Do not count a backend response as necessary for invalid form input. |
| Fresh live search | Restore RA 133.79512917, Dec −7.24514722, FOV 5 and submit. Repeat with a distinct supported field when available. | Processing progresses to at least two real observations, correct coordinates and source metadata. A 503 or timeout establishes graceful failure only, not live-search success. A known field may reuse cached cutouts. Record elapsed time and whether cache was used. |
| Archive failure | Observe an actual archive error, or use the automated mocked-error test. | Friendly error; no Python stack trace; stale images removed; retry available for retryable errors. Do not intentionally overload the archive to trigger failure. |
| Partial sequence | Open a cached entry labeled partial, if one is listed. | Loaded/skipped counts and manifest failures agree. No claim of a complete sequence. |
| Busy backend | Start a live job in one tab and submit another in a second tab while it is still running. | Second request receives a useful busy response (HTTP 429); first job remains intact. Do this once, not as a load generator. |
| API unavailable | In browser developer tools, block requests matching `*/api/*`, then reload the app. | Cached mode is explicit, live search disabled, bundled example still loads. Unblock requests and reload afterwards. Do not use whole-browser Offline for this check: it also blocks frontend assets. |
| Restart, completed session | With control of the server terminal, stop and restart the same server with the same data directory; reopen a completed session URL. | Saved images and provenance remain available. |
| Restart, active session | Requires an operator-controlled test server: start a job, obtain its ID from the POST response in the Network panel, interrupt the process, restart with the same data directory, and open `?session=ID`. | Interrupted status with original coordinates and retry. If the job finished before shutdown, ready is the correct result. A graceful stop may wait for the worker; do not mistake that for testing interruption. Do not force-kill a shared server. |

## Browser and accessibility checks

- Repeat baseline, sharing and export in Firefox and Safari where available. Chromium automation is not evidence for these browsers.
- Use a real phone/tablet if available; also test a 390 px viewport, landscape orientation and 200% browser zoom. No horizontal page scrolling or unreachable controls; labels and dates remain readable.
- Navigate with Tab/Shift+Tab. Focus must be visible, labels understandable, buttons usable with keyboard, and sliders operable with arrow keys. Drag-to-pan is currently pointer based; do not claim complete keyboard equivalence or screen-reader conformance.
- Inspect console for uncaught errors during normal use. Expected blocked network requests during failure tests are different from application crashes.
- Check long observation IDs and share URLs do not break the layout.

## Checks visual inspection cannot establish

- Correct identification of stationary reference sources and empirical registration accuracy.
- Wavelength-response, PSF, calibration and uncertainty compatibility for subtraction.
- Reliability of arbitrary sky positions or completeness of the archive query.
- Production concurrency, resource/storage limits, HTTPS configuration and host restart persistence.
- Long-duration memory use, browser support beyond tested versions, or accessibility conformance.

Treat these as separate engineering/scientific validation tasks. Keep quantitative subtraction disabled until its scientific requirements are met.
