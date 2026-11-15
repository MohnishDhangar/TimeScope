# Named astronomical targets: evidence and remaining work

The challenge's reproduced Objectives ask participants to test Barnard's Star, Epsilon Indi B, WISE 0855, RW Aurigae and R Draconis. Source: [local-event reproduction](https://hackathlone.com/challenges/planet-x-and-spherex). The official NASA page returned an error during our latest check; this is not a claim of a newly retrieved official statement.

| Target | Evidence verified for this release | Supported conclusion |
|---|---|---|
| Barnard's Star | No target-specific successful observation sequence or reproducible attempt record verified here | Target test incomplete; the user's screenshot reports a failed attempt, which needs its original log/session before claiming it as verified evidence |
| Epsilon Indi B | No target-specific sequence verified | Target test incomplete |
| WISE 0855 | Original bundled field at RA 133.79512917°, Dec −7.24514722°, width 5′; six real dated frames and original FITS provenance in its manifest | A field at the challenge-provided position can be displayed; the object's detection/motion is not established |
| RW Aurigae | No target-specific sequence verified | Target test incomplete |
| R Draconis | No target-specific sequence verified | Target test incomplete |

[Open the original field](https://timescope-331427520592.us-central1.run.app/?session=23577cd786a24f24bedec59e7c5366ae). [Original field manifest](../frontend/public/showcase/23577cd786a24f24bedec59e7c5366ae/manifest.json). The preview sequence does not supply an independent measured target identification; a chart of dates versus wavelengths is not a target light curve.

To demonstrate each target test reproducibly, retain: authoritative target identity/coordinates, coordinate epoch and applicable proper-motion treatment; exact query and UTC attempt time; deployed source/revision; discovery method and fresh/historical metadata status; selected observation IDs and dates/wavelengths; returned/usable counts; coverage/quality limitations; session/manifest and screenshot or evidence export; explicit failure class if discovery/retrieval failed. Avoid labeling an HTTP 502 as no coverage or non-detection. Archive-failed attempts establish only that a request was attempted, not that target behavior was validated.

For the current demo, show the verified bundled fields, their coordinates, dates, wavelengths and source provenance. Say that these demonstrate the temporal viewer. Do not say all five target tests passed or that WISE 0855 was detected. Full named-target validation remains unfinished, independently of the passing software/browser suites.
