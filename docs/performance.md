# Performance and resource evidence

Measured 2026-11-15 on local x86_64 Arch Linux 7.2.6, approximately 7.1 GiB total host RAM. Python 3.14.7; Astropy 8.0.2, NumPy 2.5.4, SciPy 1.18.1, reproject 0.21.0, FastAPI 0.162.7, Uvicorn 0.54.0, Astroquery 0.4.11. No container was running; controller-specific cgroup memory metrics were unavailable. None of these measurements validate Cloud Run memory or cold-start behavior.

## Five-job real-data replay

`runtime-measurements.json` contains raw results. Each job reprocessed six preserved genuine FITS cutouts from the original example, with SHA-256 verification, masks, WCS reprojection, normalization and pair diagnostics. Discovery and network retrieval were replaced by the recorded inventory and local file copies. These are five distinct processing job IDs, not five live requests to NASA.

Processing times: 0.335, 0.377, 0.329, 0.302 and 0.304 seconds. Process peak RSS stayed at 236,052 KiB (~230.5 MiB) across the five jobs. Runtime files grew from 24,257,178 to 121,285,890 bytes (~115.7 MiB). The replay used a 128 MiB aggregate cap and did not need eviction. Separate synthetic storage tests exercise pressure eviction, expiration, lease protection and capacity exhaustion. These replay times exclude application startup, discovery and network downloads; they are neither cold-cache nor warm-cache live-search latency.

Reproduce from preserved real files located OUTSIDE disposable runtime storage:

```sh
TIMESCOPE_DATA_DIR=/tmp/timescope-resource-replay \
TIMESCOPE_MAX_CACHE_MB=128 .venv/bin/python scripts/measure_runtime.py \
  /path/to/preserved/original-session --output docs/runtime-measurements.json
```

The configured release default is 512 MiB aggregate runtime storage to leave conservative reservation headroom under the planned 4 GiB container memory. This remains provisional until measured inside Cloud Run. Directory size plus RSS are diagnostics and should not be treated as an exact sum of independent physical memory.

## Actual local live attempt

`local-live-check.json` records a genuine fresh four-frame search at RA 133.79512917°, Dec −7.24514722°, FOV 5′. Both discovery routes failed. It was observed terminal at the first poll after five seconds; this is an observation bound, not an exact failure duration. No usable frames were returned. Three bundled examples remained accessible (HTTP 200). A second admission succeeded because the first job had already failed; that run therefore does not establish concurrent Busy behavior. Controlled worker tests independently verify Busy and reader access without archive traffic.

Successful cold/warm live-query latencies: **not measured**. Peak Cloud Run memory, image build performance, storage behavior in Cloud Run and background progress on Cloud Run: **not yet verified**.


## Initial Cloud Run observations

Actual remote Docker build succeeded. Cloud Monitoring `run.googleapis.com/container/memory/usage` samples for revision `timescope-00001-v78` ranged from 114,855,936 to 117,026,816 bytes at 11:22–11:24 UTC (~110–112 MiB distribution means). The two genuine public search attempts failed at discovery with HTTP 502; no calibrated FITS-processing workload completed. Consequently these memory samples must not be used as a scientific-job peak or proof of the 4 GiB resource gate. Raw data: `cloud-memory-observation.json` and `cloud-live-check.json`.


## Discovery repair allocation and current test environment

The repair session reproduced Python 3.14.7, Node 26.10.0 and npm 12.1.0. Discovery's configured default is 90 seconds (maximum 90); the public API additionally caps it at 60 seconds while retaining the one-active-job policy. The orchestrator preserves a 150-second processing reserve within the cooperative 240-second budget, usually leaving approximately 180 seconds for promptly started public jobs. These are resource allocations, not completion guarantees. Requests have bounded connect/read timeouts and cooperative stream checks; library calls cannot be forcibly interrupted.

The historical successful Cloud Run recovery job took 16.634 seconds for four fresh cutouts using saved metadata (`discovery-recovery-cloud.json`). This is not a fresh-discovery benchmark or a bound for future retrieval. The repair's one-pass local probe returned 12 HTTP 502 responses in 0.257–1.619 seconds per HTTP response; those are discovery error latencies, not scientific processing throughput. Current public repair acceptance and elapsed times will be recorded only in `discovery-repair-validation.json`. No fresh archive load tests were performed.
