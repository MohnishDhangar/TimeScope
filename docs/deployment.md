# Deployment status and operation

## Two deployment modes

- **Hosted static showcase:** real bundled SPHEREx observations, timeline, comparison, view links and standalone evidence exports. Built with `VITE_SHOWCASE_ONLY=true`. It intentionally makes no API requests and disables live coordinate search.
- **Full Python application:** built without that variable; serves the frontend and API from one origin. Requires a Python/container host and persistent writable storage. No such host is connected yet.

The hosted source checkout is `../../timescope-showcase` relative to this directory, alongside the main `timescope` project. Its `.openai/hosting.json` owns the Site identity. Reuse it for updates; do not create a duplicate Site. Frontend development remains in `timescope/frontend`; synchronize intended source changes to the showcase checkout before building and publishing. Never copy raw runtime data or credentials into the static checkout.

## Full application container

From the `timescope` directory, on a machine with Docker Compose:

```sh
docker compose up --build -d
docker compose logs -f timescope
```

The default binding is local-only: `http://127.0.0.1:8000`. A public host needs its own HTTPS ingress; this command does not create a public URL. The named `timescope-data` volume preserves sessions and download cache. Do not delete this volume when upgrading.

Environment:

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8000` | Listening port supplied by the host |
| `TIMESCOPE_DATA_DIR` | Local `data/`; `/app/data` in Docker | Persistent cache and job/session artifacts |

Run exactly one process/worker. The job lock and restart detection are not a distributed queue. The container runs as UID 10001; bind-mounted storage must be writable by that user. Keep host storage and memory limits under observation; quotas and automated retention are not implemented. `/api/health` verifies the app responds, not IRSA availability.

The bundled real-data showcase is advertised by `/api/examples` even when runtime storage is empty. The API serves its manifest under the original session ID, with previews at `/showcase/`. Loading it does not disable live coordinate search. Local sessions take precedence over bundled copies with the same identity; unknown IDs still return 404.


## Validation limits

The container definition has not been built: Docker/Podman are absent in the development environment. Direct Python startup with `PORT=8011` and a separate data directory passed an HTTP health check. This is not a substitute for a container build or a persisted-volume restart test.

The static bundle was exercised in Chromium before publication: real images, side-by-side comparison, saved-view restoration, evidence download, mobile overflow and zero API requests. The normal local suite remains separate from hosted-mode acceptance.

Before enabling public live search, verify container dependency installation, writable persistent storage, restart recovery, representative real IRSA searches, request limits and host resource behavior. The static showcase must not be described as arbitrary live sky search.


## Published release

Version 1: https://timescope-spherex.roanpaste16.chatgpt.site

Site ID: `appgprj_6af8ca4ed2c881919c82c873e04650a2`. Source commit: `9e36d3a93019dc56ee91ee9ce15a59058c6c6a97`. Deployment reported success and public access was independently checked with a fresh unauthenticated Chromium browser: HTTP 200, real-image decoding, comparison, share restoration and evidence download all passed. No account tokens were used by that browser.

## Version 3 — verified three-field gallery

Public URL unchanged: https://timescope-spherex.roanpaste16.chatgpt.site

Source commit: `338223e4502306d9ae093a8335cf9977ebfbc8f4`. Published version 3. Fresh unauthenticated Chromium verified BOTH new fields: decoded real previews, correct loaded coordinates, side-by-side comparison, evidence downloads and shared-view restoration. Mobile layout had no horizontal overflow and no page errors occurred. Screenshots are under local `data/gallery-public-*.png`.

This completes publication of the additional-examples milestone. The hosted site still intentionally disables live coordinate searches; the retrieval improvements run in the local Python backend.

## Version 4 — comparison workspace

Source commit `5e0d5c6562af7d39e5633285c11c6cf12892b387`. Public URL unchanged. Includes time/wavelength chart, automatic selected-pair blinking and exportable comparison evidence. Public Chromium smoke check verified these interactions on real bundled observations. No hosted live search or quantitative subtraction is implied.

## Superseding deployment decision

The master task selects Google Cloud Run with ephemeral sessions. See [CLOUD-DEPLOYMENT.md](CLOUD-DEPLOYMENT.md) for the authoritative current configuration and status. Earlier persistent-volume and provider guidance in this document is historical.
