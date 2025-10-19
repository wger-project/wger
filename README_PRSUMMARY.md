# PMOVES Integration – Wger Docker + GHCR

This PR adds:
- A GitHub Actions workflow to publish a multi‑arch Docker image to GHCR on pushes to `main` and on semver tags.
- A minimal `docker-compose.pmoves-net.yml` that attaches the service to the shared `pmoves-net` network for first‑class PMOVES integration.

Usage (local):
```bash
docker network create pmoves-net || true
docker compose -f docker-compose.pmoves-net.yml up -d
# UI: http://localhost:8000
```

The image will be published as `ghcr.io/POWERFULMOVES/Pmoves-Health-wger:main` (and tags). PMOVES can pull this via its external compose.

Notes:
- Ensure a `Dockerfile` exists at repo root or update the workflow `context` accordingly.
- If environment/config is required for admin bootstrap, document variables in this README.
