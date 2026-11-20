# 001: v1 stack — Django monolith, templates + HTMX, Postgres

Status: Accepted (2026-11-19)

## Context
LogIt is a solo portfolio project whose most important part is the topic-suggestion search and
its offline evaluation. The stack has to make CRUD (auth, lists, entries) cheap so time goes to
search, and has to be explainable end to end in an interview.

## Options
1. Django monolith, server-rendered templates + HTMX, Postgres.
2. FastAPI backend + React/Next.js frontend, Postgres.
3. Next.js full-stack (TypeScript) + Postgres via Prisma/Drizzle.

## Choice
Option 1. One Django project with apps `accounts`, `catalog`, `lists`, `search` (added as slices
need them) plus `core` for infrastructure. Postgres from day one with `pg_trgm`; `pgvector` is
added at the embeddings phase. pytest + pytest-django, ruff, mypy (strict, django-stubs), Docker
Compose for local dev, GitHub Actions CI.

## Why
- **Django:** auth, admin, ORM, and migrations are built in, which removes the most bug-prone
  boilerplate (password hashing, sessions, CSRF). Python also matches the ML side (sentence-transformers, eval notebooks) so
  the search code and the app share one language and one test suite.
- **Templates + HTMX over a SPA:** one deployable, no API contract to keep in sync, and no
  client-side state for a mostly read-and-form app. Tradeoff: richer interactions (drag-to-reorder,
  offline mobile) are harder; a JSON API can be added beside the templates if the mobile app happens.
- **Postgres from day one, not SQLite:** trigram search and vector search are Postgres
  extensions, and the eval must run against the same engine as production. Tradeoff: local setup
  needs Docker or a Postgres install instead of zero-setup SQLite.
- **Monolith with modular apps:** one process is the simplest thing to run, debug, and deploy.
  Service-layer modules per app keep boundaries clear enough that `search` could be split into
  its own service later.

## Supporting choices
- **Config from environment variables only** (`django-environ`): the same code runs locally, in
  Docker, CI, and the cloud. `DJANGO_SECRET_KEY` and `DATABASE_URL` have no defaults, so a
  misconfigured deploy fails at startup instead of running with a dev secret.
- **Structured logging (`structlog`) with request IDs:** one JSON line per event, with a
  `request_id` that is also returned in the `X-Request-ID` header. Upstream IDs are accepted only if they
  match `[A-Za-z0-9._-]{1,64}`, to prevent log injection. Sentry/OpenTelemetry can attach to this
  pipeline later without touching call sites.
- **Pinned `requirements*.txt` + pip, no lockfile tool:** fewest moving parts. Tradeoff: indirect
  dependencies aren't locked, so builds can drift; switch to `uv` or `pip-tools` if that bites.
- **CI runs `makemigrations --check`:** a model change without a migration fails the build.
- **Postgres 18** in Compose and CI, matching the locally installed version.

## Rejected
- **FastAPI + React:** more architecture to show, but it doubles the surface (two apps, an API
  schema, auth tokens or CORS) and delays the search work, which is the point of the project.
- **Next.js full stack:** strong for frontend roles, but the ML/eval half would live in a second
  language anyway.
- **SQLite for dev:** no `pg_trgm` or `pgvector`, so search behavior would differ between dev and
  prod.

## At 100x scale
The monolith still holds; the first pressures are elsewhere. Embedding work moves to background
tasks (Celery + Redis), the embedding model moves to its own service (the `Embedder` interface is
the seam for that), the database gets read replicas and HNSW/IVFFlat index tuning, and the app
runs as multiple stateless containers behind a load balancer (sessions are already DB-backed).
