# AI log

What Claude did, what Neel reviewed or rewrote, and what Claude got wrong. Newest first.

## 2026-11-19 — Slice 0: project skeleton + custom User model

**Claude did**
- Django 5.2 project (`config/`), apps `core` and `accounts`, settings read entirely from env vars.
- Custom `User` (UUID pk, case-insensitive unique username, lowercase-enforced email, reserved
  names) + `register_user` service + admin. See ADR 002.
- `pg_trgm` migration, request-ID middleware, structlog JSON logging.
- Dockerfile, docker-compose (Postgres 18), GitHub Actions CI (ruff, ruff format, mypy strict,
  `makemigrations --check`, pytest).
- Moved `src/users/logic.txt` → `docs/notes/users.md`; deleted the empty `src/users/models.py`.
- ADRs 001 (stack) and 002 (custom user).

**Verified (real results)**
- `pytest`: 27 passed (before trimming, see below), against a throwaway local Postgres 18.1 cluster (not Docker; Docker isn't
  installed on this machine yet).
- `ruff check`, `ruff format --check`, `mypy` (strict): clean. `makemigrations --check`: no changes.
- **Not verified yet:** `docker compose up` and the GitHub Actions run (Docker not installed, nothing pushed).

**Claude got wrong (caught by tests/tools)**
- Subscripted Django form/manager generics (`UserCreationForm[User]`) without the
  `django-stubs-ext` runtime patch, so the app crashed at import. Fixed by dropping the subscripts
  and adding `# type: ignore[type-arg]` instead of adding a runtime dependency.
- `register_user` relied on `Model.clean()` to trim the email, but field validators run *before*
  `clean()`, so `"  Neel@Example.COM "` was rejected as invalid. Fixed by normalizing in the
  service before validation; the test caught it.

- While trimming, Claude cut email lowercasing down to `register_user` only. Running the app
  showed `createsuperuser --email Boss@Example.com` crashed with an IntegrityError: Django's
  `create_user` only lowercases the domain, so the DB check rejected the row. The unit tests
  didn't catch it because they only covered `register_user`. Fixed by overriding
  `UserManager.normalize_email`, the hook that `create_user`, `create_superuser`, and
  `Model.clean()` (forms, admin) all call. Added a test for it.

**Manual run (live server, fresh Postgres 18 DB)**
- `createsuperuser` with a mixed-case email works; stored as `boss@example.com`.
- Admin: wrong password rejected; login works; adding users works; the add form rejects a
  case-duplicate username, a reserved name, a bad format, and a case-duplicate email; a mixed-case
  email is stored lowercase.
- `X-Request-ID`: generated, reused when safe, replaced when unsafe; JSON log lines (ours and
  Django's) carry the ID.
- A missing `DJANGO_SECRET_KEY` fails at startup with `ImproperlyConfigured`.
- Known gap: `runserver`'s own access lines (`"GET /admin/ HTTP/1.1" 302`) are plain text; that
  logger only exists in the dev server.

**Pre-commit review (asked: concise and tested)**
- Removed leftovers: settings that restated Django defaults, a stale `staticfiles/` ignore,
  an unused pytest option and mypy override, extra Dockerfile env vars, the DB host port, `.env`
  indirection in Compose, and a duplicate `pull_request` CI trigger.
- Added tests for things only checked by hand before: adding a user in the admin, the UUID id,
  and that log lines (ours and Django's) are JSON with the request ID.
- Claude's first JSON-log test used `capfd` and failed: Django configures logging while pytest's
  capture is active, so the handler writes to pytest's file, not stderr. Rewrote it to render
  the captured records with the app's own formatter.
- Checked the new tests catch real bugs by breaking the code on purpose (dropping the request
  ID from logs, removing email from the admin form, using Django's default email normalizing,
  un-reserving "admin"): each break failed at least one test; code restored after.
- Result: 16 tests passed; ruff, ruff format, mypy, and `makemigrations --check` clean.

**Neel reviewed / rewrote**
- Asked for minimal, easy-to-understand changes. Claude had added things nobody asked for, so it
  trimmed Slice 0 before the first commit:
  - removed the `/healthz` endpoint (tests use any URL);
  - removed the case-insensitive login manager (deferred to Slice 1);
  - email lowercasing now happens in one place (`register_user`) plus the DB check, not in
    `save()` and `clean()` too;
  - removed the custom admin forms (Django's `UserAdmin` already works with an `AbstractUser`
    subclass; verified that adding a user in the admin works) and the `display_name` argument;
  - removed the console/JSON log-format switch (JSON only) and the request timing field;
  - cut the reserved-names list to 7 and the tests from 27 to 14.
- After trimming and the fix below: 15 tests passed; ruff, ruff format, mypy, and `makemigrations --check` clean.
